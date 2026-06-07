"""
Motor de Asignación Inteligente + Sistema de Priorización.
Calcula prioridades según clasificación IA, busca talleres candidatos usando PostGIS,
y asigna automáticamente al taller más cercano con técnico disponible.
"""
from __future__ import annotations

import asyncio
import logging
from math import asin, cos, radians, sin, sqrt
from uuid import UUID

from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from app.models.models import INCIDENTES, TALLERES, TECNICOS, ASIGNACIONES

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
            from app.application.use_cases.notification_service import broadcast_global
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
