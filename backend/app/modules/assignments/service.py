"""
Motor de Asignación Inteligente + Sistema de Priorización.
Calcula prioridades según clasificación IA, busca talleres candidatos usando PostGIS,
y asigna automáticamente al taller más cercano con técnico disponible.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from uuid import UUID

from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from app.models.models import INCIDENTES, HISTORIAL_INCIDENTES
from app.modules.assignments.models import ASIGNACIONES
from app.modules.technicians.models import TECNICOS
from app.modules.workshops.models import TALLERES

logger = logging.getLogger(__name__)

# Mapeo de clasificación IA a prioridad
PRIORIDAD_POR_CLASIFICACION = {
    "CHOQUE": "ALTA",
    "MOTOR": "ALTA",
    "BATERIA": "MEDIA",
    "LLANTA": "MEDIA",
    "OTROS": "BAJA",
    "INCIERTO": "BAJA",
}

# Radio de búsqueda en km para PostGIS
RADIO_BUSQUEDA_KM = 50

# Radio (km) preferente para mostrar ofertas de talleres cercanos al cliente.
RADIO_OFERTAS_KM = 25
# Tope absoluto: nunca ofrecer talleres más lejos que esto (evita precios
# absurdos por coordenadas erróneas). Si ninguno cae dentro, no hay ofertas.
RADIO_MAX_KM = 80
MAX_OFERTAS_FALLBACK = 5


def calcular_prioridad(incidente: INCIDENTES) -> str:
    """
    Calcula la prioridad del incidente según su clasificación IA.

    :param incidente: Modelo ORM del incidente
    :return: Nivel de prioridad ("ALTA", "MEDIA", "BAJA")
    """
    clasificacion = incidente.CLASIFICACION
    if clasificacion:
        clasificacion_str = (
            clasificacion.value if hasattr(clasificacion, "value") else str(clasificacion)
        )
        return PRIORIDAD_POR_CLASIFICACION.get(clasificacion_str, "BAJA")
    return "BAJA"


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two WGS84 points."""
    r = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return 2 * r * asin(sqrt(a))


def buscar_talleres_candidatos(db: Session, incidente: INCIDENTES) -> list[dict]:
    """
    Busca técnicos elegibles y los ordena por cercanía del taller al incidente.

    Reglas:
    - Solo técnicos DISPONIBLES con cuenta móvil (ID_USUARIO no nulo): así la
      notificación de asignación les llega al teléfono.
    - Solo talleres ACTIVOS.
    - Orden por distancia (haversine) entre el incidente y la ubicación fija del
      taller (LATITUD/LONGITUD). Talleres sin coordenadas quedan al final.

    :return: Lista de dicts {id_taller, id_tecnico, distancia_km, taller} (más cercano primero).
    """
    if incidente.UBICACION is None:
        logger.warning("Incidente %s sin ubicación", incidente.ID_INCIDENTE)
        return []

    try:
        punto_incidente = to_shape(incidente.UBICACION)
        lat_incidente = punto_incidente.y
        lon_incidente = punto_incidente.x
    except Exception:
        logger.exception("No se pudo leer la ubicación del incidente %s", incidente.ID_INCIDENTE)
        return []

    filas = (
        db.query(TALLERES, TECNICOS)
        .join(TECNICOS, TALLERES.ID_TALLER == TECNICOS.ID_TALLER)
        .filter(
            TALLERES.ACTIVO.is_(True),
            TECNICOS.DISPONIBLE.is_(True),
            TECNICOS.ID_USUARIO.isnot(None),  # solo técnicos con cuenta móvil
        )
        .all()
    )

    candidatos = []
    for taller, tecnico in filas:
        if taller.LATITUD is not None and taller.LONGITUD is not None:
            distancia = _haversine_km(
                lat_incidente, lon_incidente, float(taller.LATITUD), float(taller.LONGITUD)
            )
        else:
            distancia = float("inf")  # sin coords: que quede al final del orden
        candidatos.append({
            "id_taller": taller.ID_TALLER,
            "id_tecnico": tecnico.ID_TECNICO,
            "distancia_km": distancia,
            "taller": taller,
        })

    candidatos.sort(key=lambda c: c["distancia_km"])
    for c in candidatos:
        if c["distancia_km"] == float("inf"):
            c["distancia_km"] = 0.0  # normalizar para logging/persistencia

    logger.debug(
        "Encontrados %d candidatos (con cuenta móvil) para incidente %s",
        len(candidatos),
        incidente.ID_INCIDENTE,
    )
    return candidatos


def asignar_taller_automaticamente(db: Session, incidente_id: UUID) -> ASIGNACIONES | None:
    """
    Busca el taller más cercano con técnico disponible y asigna automáticamente.
    Actualiza el estado del incidente a "ASIGNADO".

    :param db: Sesión de base de datos
    :param incidente_id: UUID del incidente
    :return: Objeto ASIGNACIONES creado, o None si no hay candidatos
    """
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == incidente_id).first()
    if not incidente:
        logger.warning("Incidente %s no encontrado", incidente_id)
        return None

    # Actualizar prioridad si es necesario
    nueva_prioridad = calcular_prioridad(incidente)
    if incidente.PRIORIDAD != nueva_prioridad:
        incidente.PRIORIDAD = nueva_prioridad
        db.add(incidente)
        db.flush()

    # Buscar candidatos
    candidatos = buscar_talleres_candidatos(db, incidente)
    if not candidatos:
        logger.warning("No hay talleres candidatos para incidente %s", incidente_id)
        return None

    # Seleccionar el más cercano (ya ordenado por distancia)
    candidato_elegido = candidatos[0]
    id_taller = candidato_elegido["id_taller"]
    id_tecnico = candidato_elegido["id_tecnico"]
    distancia_km = candidato_elegido["distancia_km"]

    try:
        # Marcar técnico como no disponible en la misma transacción
        tecnico = db.query(TECNICOS).filter(TECNICOS.ID_TECNICO == id_tecnico).first()
        if tecnico:
            tecnico.DISPONIBLE = False
            db.add(tecnico)

        asignacion = ASIGNACIONES(
            ID_INCIDENTE=incidente_id,
            ID_TALLER=id_taller,
            ID_TECNICO=id_tecnico,
        )

        # Cotización automática (precio generado por reglas, no por el taller).
        from app.modules.payments import service as payment_service
        clasificacion_txt = (
            incidente.CLASIFICACION.value if hasattr(incidente.CLASIFICACION, "value")
            else str(incidente.CLASIFICACION)
        )
        monto, _comision, detalle = payment_service.cotizar(clasificacion_txt, nueva_prioridad)
        asignacion.MONTO_COTIZADO = monto
        asignacion.NOTAS_COTIZACION = detalle
        db.add(asignacion)

        incidente.ESTADO = "ASIGNADO"
        db.add(incidente)

        db.commit()
        db.refresh(asignacion)

        logger.info(
            "Incidente %s asignado a taller %s (distancia: %.2f km)",
            incidente_id,
            id_taller,
            distancia_km,
        )

        # Notificar en tiempo real al panel (Dashboard/Mapa/Talleres) que hay
        # una nueva asignación, para que el taller la vea sin recargar.
        taller_obj = candidato_elegido.get("taller")
        notif = {
            "tipo": "nueva_asignacion",
            "incidente_id": str(incidente_id),
            "asignacion_id": str(asignacion.ID_ASIGNACION),
            "taller_id": str(id_taller),
            "taller_nombre": getattr(taller_obj, "NOMBRE_NEGOCIO", None),
            "tecnico_id": str(id_tecnico),
            "tecnico_nombre": getattr(tecnico, "NOMBRE_COMPLETO", None) if tecnico else None,
            "mensaje": "Nuevo incidente asignado a tu taller",
        }
        try:
            from app.modules.notifications.service import broadcast_global
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(broadcast_global(notif))
        except Exception:
            logger.exception("No se pudo emitir nueva_asignacion para incidente %s", incidente_id)

        return asignacion

    except Exception:
        logger.exception("Error al asignar incidente %s", incidente_id)
        db.rollback()
        return None


def generar_ofertas(
    db: Session, incidente: INCIDENTES, radio_km: float = RADIO_OFERTAS_KM
) -> list[dict]:
    """
    Genera las ofertas de talleres cercanos para que el cliente elija (estilo
    InDrive). Un taller por oferta, cada uno con su precio según ubicación, hora
    y problema, más una descripción del cálculo.

    :return: lista de dicts {id_taller, nombre_taller, distancia_km, monto,
             descripcion, id_tecnico_sugerido}, ordenada por distancia.
    """
    from app.modules.payments import service as payment_service

    nueva_prioridad = calcular_prioridad(incidente)
    clasif = (
        incidente.CLASIFICACION.value if hasattr(incidente.CLASIFICACION, "value")
        else str(incidente.CLASIFICACION)
    )
    candidatos = buscar_talleres_candidatos(db, incidente)

    # Un técnico por taller (el más cercano ya viene primero); requiere coords.
    por_taller: list[dict] = []
    vistos: set = set()
    for c in candidatos:
        taller = c["taller"]
        if c["id_taller"] in vistos:
            continue
        if taller.LATITUD is None or taller.LONGITUD is None:
            continue
        vistos.add(c["id_taller"])
        por_taller.append(c)

    dentro_radio = [c for c in por_taller if c["distancia_km"] <= radio_km]
    if dentro_radio:
        elegidos = dentro_radio
    else:
        # Fallback acotado: los más cercanos, pero nunca más lejos que el tope.
        elegidos = [c for c in por_taller if c["distancia_km"] <= RADIO_MAX_KM][:MAX_OFERTAS_FALLBACK]

    ofertas: list[dict] = []
    for c in elegidos:
        taller = c["taller"]
        dist = c["distancia_km"]
        monto, descripcion = payment_service.cotizar_oferta(clasif, nueva_prioridad, dist)
        ofertas.append({
            "id_taller": str(c["id_taller"]),
            "nombre_taller": taller.NOMBRE_NEGOCIO,
            "distancia_km": round(dist, 1),
            "monto": float(monto),
            "descripcion": descripcion,
            "id_tecnico_sugerido": str(c["id_tecnico"]),
        })
    return ofertas


def seleccionar_taller(
    db: Session, incidente_id: UUID, id_taller: UUID
) -> ASIGNACIONES | None:
    """
    El cliente elige un taller de las ofertas. Asigna automáticamente un técnico
    disponible (con cuenta móvil) de ese taller, fija la cotización del taller
    elegido y pasa el incidente directamente a EN_CAMINO.

    :return: ASIGNACIONES creada; None si no hay incidente o técnico disponible.
    """
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == incidente_id).first()
    if not incidente:
        logger.warning("Incidente %s no encontrado al seleccionar taller", incidente_id)
        return None

    # Idempotencia: si ya hay una asignación activa, devolverla sin duplicar.
    existente = (
        db.query(ASIGNACIONES)
        .filter(ASIGNACIONES.ID_INCIDENTE == incidente_id, ASIGNACIONES.FECHA_RECHAZO.is_(None))
        .first()
    )
    if existente:
        return existente

    tecnico = (
        db.query(TECNICOS)
        .filter(
            TECNICOS.ID_TALLER == id_taller,
            TECNICOS.DISPONIBLE.is_(True),
            TECNICOS.ID_USUARIO.isnot(None),
        )
        .first()
    )
    if not tecnico:
        logger.warning("Taller %s sin técnico disponible para incidente %s", id_taller, incidente_id)
        return None

    taller = db.query(TALLERES).filter(TALLERES.ID_TALLER == id_taller).first()

    # Distancia para reproducir la misma cotización que vio el cliente.
    distancia_km = 0.0
    try:
        if taller and taller.LATITUD is not None and taller.LONGITUD is not None and incidente.UBICACION is not None:
            punto = to_shape(incidente.UBICACION)
            distancia_km = _haversine_km(
                punto.y, punto.x, float(taller.LATITUD), float(taller.LONGITUD)
            )
    except Exception:
        logger.exception("No se pudo calcular distancia al seleccionar taller %s", id_taller)

    from app.modules.payments import service as payment_service
    nueva_prioridad = calcular_prioridad(incidente)
    clasif = (
        incidente.CLASIFICACION.value if hasattr(incidente.CLASIFICACION, "value")
        else str(incidente.CLASIFICACION)
    )
    monto, descripcion = payment_service.cotizar_oferta(clasif, nueva_prioridad, distancia_km)

    try:
        tecnico.DISPONIBLE = False
        db.add(tecnico)

        asignacion = ASIGNACIONES(
            ID_INCIDENTE=incidente_id,
            ID_TALLER=id_taller,
            ID_TECNICO=tecnico.ID_TECNICO,
            MONTO_COTIZADO=monto,
            NOTAS_COTIZACION=descripcion,
        )
        db.add(asignacion)

        incidente.PRIORIDAD = nueva_prioridad
        incidente.ESTADO = "EN_CAMINO"
        db.add(incidente)
        db.flush()

        db.add(
            HISTORIAL_INCIDENTES(
                ID_INCIDENTE=incidente_id,
                ESTADO="EN_CAMINO",
                NOTAS=f"Cliente eligió taller {getattr(taller, 'NOMBRE_NEGOCIO', '')}. {descripcion}",
                ID_USUARIO_CAMBIO=None,
            )
        )

        db.commit()
        db.refresh(asignacion)
    except Exception:
        logger.exception("Error al seleccionar taller %s para incidente %s", id_taller, incidente_id)
        db.rollback()
        return None

    # Notificar a todos los canales (cliente móvil incluido) el paso a EN_CAMINO,
    # para que arranque el seguimiento en tiempo real del técnico.
    try:
        from app.modules.notifications.service import broadcast_estado_actualizado
        broadcast_estado_actualizado(db, incidente_id, "EN_CAMINO")
    except Exception:
        logger.exception("No se pudo emitir estado EN_CAMINO para incidente %s", incidente_id)

    return asignacion


# Estados en los que cancelar implica multa (el técnico ya fue despachado).
ESTADOS_CON_MULTA = {"EN_CAMINO", "EN_PROCESO"}


def cancelar_por_cliente(db: Session, incidente_id: UUID) -> dict | None:
    """
    Cancela el servicio a pedido del cliente.

    - Libera al técnico (DISPONIBLE = True) y marca la asignación como cancelada.
    - Si el técnico ya estaba en camino/en proceso, aplica una multa del 20%.
    - Pasa el incidente a CANCELADO, notifica al técnico y a todos los canales.

    :return: dict {con_penalidad, monto_multa, estado_anterior} o None si no existe.
    """
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == incidente_id).first()
    if not incidente:
        return None

    estado_anterior = (
        incidente.ESTADO.value if hasattr(incidente.ESTADO, "value") else str(incidente.ESTADO)
    )
    con_penalidad = estado_anterior in ESTADOS_CON_MULTA

    asignacion = (
        db.query(ASIGNACIONES)
        .filter(ASIGNACIONES.ID_INCIDENTE == incidente_id, ASIGNACIONES.FECHA_RECHAZO.is_(None))
        .first()
    )

    monto_multa = 0.0
    try:
        # Liberar al técnico asignado.
        if asignacion and asignacion.ID_TECNICO:
            tecnico = db.query(TECNICOS).filter(TECNICOS.ID_TECNICO == asignacion.ID_TECNICO).first()
            if tecnico:
                tecnico.DISPONIBLE = True
                db.add(tecnico)

        # Multa si el servicio ya estaba en camino/proceso.
        if con_penalidad:
            from app.modules.payments import service as payment_service
            multa = payment_service.crear_multa_cancelacion(db, incidente, asignacion)
            monto_multa = float(multa.MONTO)

        # Marcar la asignación como cerrada por cancelación.
        if asignacion:
            asignacion.FECHA_RECHAZO = datetime.now(timezone.utc)
            asignacion.MOTIVO_RECHAZO = "Cancelado por el cliente"
            db.add(asignacion)

        incidente.ESTADO = "CANCELADO"
        db.add(incidente)

        db.add(
            HISTORIAL_INCIDENTES(
                ID_INCIDENTE=incidente_id,
                ESTADO="CANCELADO",
                NOTAS=(
                    "Cancelado por el cliente."
                    + (f" Multa aplicada: Bs.{monto_multa}." if con_penalidad else "")
                ),
                ID_USUARIO_CAMBIO=incidente.ID_USUARIO_CLIENTE,
            )
        )

        db.commit()
        db.refresh(incidente)
    except Exception:
        logger.exception("Error al cancelar incidente %s por el cliente", incidente_id)
        db.rollback()
        return None

    # Notificaciones: estado CANCELADO a todos + aviso/cierre al técnico.
    try:
        from app.modules.notifications.service import (
            broadcast_estado_actualizado,
            notificar_cancelacion_tecnico,
        )
        broadcast_estado_actualizado(db, incidente_id, "CANCELADO")
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(notificar_cancelacion_tecnico(incidente_id))
    except Exception:
        logger.exception("No se pudo notificar la cancelación del incidente %s", incidente_id)

    return {
        "con_penalidad": con_penalidad,
        "monto_multa": monto_multa,
        "estado_anterior": estado_anterior,
    }
