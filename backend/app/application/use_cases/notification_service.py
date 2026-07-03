"""
Sistema de Notificaciones + Seguimiento en Tiempo Real.
Gestiona notificaciones push a clientes y talleres, y mantiene conexiones WebSocket activas.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from uuid import UUID
from typing import Callable, Any

from sqlalchemy.orm import Session
from fastapi import WebSocket

from app.models.models import INCIDENTES
from app.modules.users.models import USUARIOS

logger = logging.getLogger(__name__)

# Diccionario global de conexiones WebSocket activas
# Estructura: {incidente_id: [WebSocket, ...]}
CONEXIONES_ACTIVAS: dict[UUID, list[WebSocket]] = {}

# Lista global de conexiones WebSocket (Dashboard, Mapa, etc.)
CONEXIONES_GLOBALES: list[WebSocket] = []

# Un WebSocket por incidente — el técnico asignado transmite su ubicación GPS en tiempo real
CONEXIONES_TECNICO: dict[UUID, WebSocket] = {}


def registrar_conexion_global(websocket: WebSocket) -> None:
    CONEXIONES_GLOBALES.append(websocket)


def desregistrar_conexion_global(websocket: WebSocket) -> None:
    try:
        CONEXIONES_GLOBALES.remove(websocket)
    except ValueError:
        pass


EVENTOS_IMPORTANTES = {
    "estado_actualizado",
    "incidente_reportado",
    "nueva_asignacion",
    "nuevo_usuario",
    "pago_pendiente",
    "pago_confirmado",
    "pago_rechazado",
}

# Estados que gestiona el pipeline IA internamente — no notificar al Dashboard/Mapa
ESTADOS_INTERNOS = {"EN_PROCESO_IA", "CLASIFICADO", "PENDIENTE"}


async def broadcast_global(datos: dict) -> None:
    """Envía un evento a TODAS las conexiones globales activas (solo eventos relevantes)."""
    tipo = datos.get("tipo", "")
    if tipo not in EVENTOS_IMPORTANTES:
        return
    if tipo == "estado_actualizado" and datos.get("nuevo_estado", "") in ESTADOS_INTERNOS:
        return
    fallidas = []
    for ws in CONEXIONES_GLOBALES:
        try:
            await ws.send_json(datos)
        except Exception:
            fallidas.append(ws)
    for ws in fallidas:
        desregistrar_conexion_global(ws)

# Callbacks para enviar notificaciones (pueden integrarse con push services reales)
NOTIFICACION_CALLBACKS: dict[str, list[Callable[[dict[str, Any]], None]]] = {
    "cliente": [],
    "taller": [],
    "broadcast": [],
}


def registrar_callback_notificacion(tipo: str, callback: Callable) -> None:
    """
    Registra un callback para enviar notificaciones (ej. push services reales).

    :param tipo: "cliente", "taller" o "broadcast"
    :param callback: Función que recibe el dict de notificación
    """
    if tipo in NOTIFICACION_CALLBACKS:
        NOTIFICACION_CALLBACKS[tipo].append(callback)
        logger.debug("Callback registrado para notificaciones de %s", tipo)


def enviar_notificacion_cliente(db: Session, incidente_id: UUID, mensaje: str) -> None:
    """
    Envía notificación al cliente propietario del incidente.

    :param db: Sesión de base de datos
    :param incidente_id: UUID del incidente
    :param mensaje: Mensaje de notificación
    """
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == incidente_id).first()
    if not incidente:
        logger.warning("Incidente %s no encontrado para notificación cliente", incidente_id)
        return

    usuario_cliente = (
        db.query(USUARIOS)
        .filter(USUARIOS.ID_USUARIO == incidente.ID_USUARIO_CLIENTE)
        .first()
    )
    if not usuario_cliente:
        logger.warning("Usuario cliente no encontrado para incidente %s", incidente_id)
        return

    notificacion = {
        "tipo": "notificacion_cliente",
        "incidente_id": str(incidente_id),
        "usuario_id": str(usuario_cliente.ID_USUARIO),
        "mensaje": mensaje,
        "estado_incidente": (
            incidente.ESTADO.value if hasattr(incidente.ESTADO, "value")
            else str(incidente.ESTADO)
        ),
        "prioridad": (
            incidente.PRIORIDAD.value if hasattr(incidente.PRIORIDAD, "value")
            else str(incidente.PRIORIDAD)
        ),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Ejecutar callbacks registrados
    for callback in NOTIFICACION_CALLBACKS["cliente"]:
        try:
            callback(notificacion)
        except Exception:
            logger.exception("Error en callback de notificación cliente")

    # Broadcast por WebSocket
    _broadcast_incidente(incidente_id, notificacion)

    logger.info(
        "Notificación de cliente enviada: incidente %s, usuario %s",
        incidente_id,
        usuario_cliente.ID_USUARIO,
    )


def enviar_notificacion_taller(db: Session, incidente_id: UUID, mensaje: str) -> None:
    """
    Envía notificación al taller asignado del incidente.

    :param db: Sesión de base de datos
    :param incidente_id: UUID del incidente
    :param mensaje: Mensaje de notificación
    """
    from app.models.models import ASIGNACIONES
    from app.modules.workshops.models import TALLERES

    asignacion = (
        db.query(ASIGNACIONES)
        .filter(ASIGNACIONES.ID_INCIDENTE == incidente_id)
        .first()
    )
    if not asignacion:
        logger.warning("Asignación no encontrada para incidente %s", incidente_id)
        return

    taller = db.query(TALLERES).filter(TALLERES.ID_TALLER == asignacion.ID_TALLER).first()
    if not taller:
        logger.warning("Taller no encontrado para asignación %s", asignacion.ID_ASIGNACION)
        return

    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == incidente_id).first()

    notificacion = {
        "tipo": "notificacion_taller",
        "incidente_id": str(incidente_id),
        "taller_id": str(taller.ID_TALLER),
        "asignacion_id": str(asignacion.ID_ASIGNACION),
        "mensaje": mensaje,
        "estado_incidente": (
            incidente.ESTADO.value if hasattr(incidente.ESTADO, "value")
            else str(incidente.ESTADO)
        ),
        "clasificacion": (
            incidente.CLASIFICACION.value if hasattr(incidente.CLASIFICACION, "value")
            else str(incidente.CLASIFICACION)
        ),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Ejecutar callbacks registrados
    for callback in NOTIFICACION_CALLBACKS["taller"]:
        try:
            callback(notificacion)
        except Exception:
            logger.exception("Error en callback de notificación taller")

    # Broadcast por WebSocket
    _broadcast_incidente(incidente_id, notificacion)

    logger.info(
        "Notificación de taller enviada: incidente %s, taller %s",
        incidente_id,
        taller.ID_TALLER,
    )


def broadcast_estado_actualizado(
    db: Session, incidente_id: UUID, nuevo_estado: str
) -> None:
    """
    Notifica a clientes y talleres sobre cambio de estado del incidente.

    :param db: Sesión de base de datos
    :param incidente_id: UUID del incidente
    :param nuevo_estado: Nuevo estado del incidente
    """
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == incidente_id).first()
    if not incidente:
        logger.warning("Incidente %s no encontrado para broadcast", incidente_id)
        return

    mensaje = f"Estado actualizado: {nuevo_estado}"

    notificacion = {
        "tipo": "estado_actualizado",
        "incidente_id": str(incidente_id),
        "nuevo_estado": nuevo_estado,
        "mensaje": mensaje,
        "prioridad": (
            incidente.PRIORIDAD.value if hasattr(incidente.PRIORIDAD, "value")
            else str(incidente.PRIORIDAD)
        ),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Ejecutar callbacks de broadcast
    for callback in NOTIFICACION_CALLBACKS["broadcast"]:
        try:
            callback(notificacion)
        except Exception:
            logger.exception("Error en callback de broadcast")

    # Broadcast por WebSocket
    _broadcast_incidente(incidente_id, notificacion)

    # Notificar al cliente
    try:
        enviar_notificacion_cliente(db, incidente_id, mensaje)
    except Exception:
        logger.exception("Error al notificar cliente en broadcast")

    # Notificar al taller si está asignado
    if nuevo_estado in ["EN_CAMINO", "EN_PROCESO", "ATENDIDO", "CANCELADO"]:
        try:
            enviar_notificacion_taller(db, incidente_id, mensaje)
        except Exception:
            logger.exception("Error al notificar taller en broadcast")

    # Notificar también a todas las conexiones globales (Dashboard, Mapa)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_global(notificacion))
    except Exception:
        logger.exception("Error en broadcast global")

    logger.info("Broadcast de estado enviado: incidente %s, estado %s", incidente_id, nuevo_estado)


async def broadcast_incidente_async(incidente_id: UUID, datos: dict) -> None:
    """Envía datos a todos los WebSocket suscritos a un incidente (versión async)."""
    conexiones = CONEXIONES_ACTIVAS.get(incidente_id, [])
    fallidas = []
    for ws in list(conexiones):
        try:
            await ws.send_json(datos)
        except Exception:
            logger.debug("WS caído para incidente %s — se descarta", incidente_id)
            fallidas.append(ws)
    for ws in fallidas:
        try:
            conexiones.remove(ws)
        except ValueError:
            pass
    if incidente_id in CONEXIONES_ACTIVAS and not CONEXIONES_ACTIVAS[incidente_id]:
        del CONEXIONES_ACTIVAS[incidente_id]


def _broadcast_incidente(incidente_id: UUID, datos: dict) -> None:
    """Wrapper síncrono — encola la coroutine en el event loop activo."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_incidente_async(incidente_id, datos))
    except Exception:
        logger.exception("Error al encolar broadcast para incidente %s", incidente_id)


def registrar_conexion_websocket(incidente_id: UUID, websocket: WebSocket) -> None:
    """
    Registra una nueva conexión WebSocket para un incidente.

    :param incidente_id: UUID del incidente
    :param websocket: Objeto WebSocket
    """
    if incidente_id not in CONEXIONES_ACTIVAS:
        CONEXIONES_ACTIVAS[incidente_id] = []
    CONEXIONES_ACTIVAS[incidente_id].append(websocket)
    logger.debug("WebSocket registrado para incidente %s", incidente_id)


def desregistrar_conexion_websocket(incidente_id: UUID, websocket: WebSocket) -> None:
    """
    Desregistra una conexión WebSocket.

    :param incidente_id: UUID del incidente
    :param websocket: Objeto WebSocket
    """
    if incidente_id in CONEXIONES_ACTIVAS:
        try:
            CONEXIONES_ACTIVAS[incidente_id].remove(websocket)
        except ValueError:
            pass

        if not CONEXIONES_ACTIVAS[incidente_id]:
            del CONEXIONES_ACTIVAS[incidente_id]

    logger.debug("WebSocket desregistrado para incidente %s", incidente_id)


def tiene_tracking_activo(incidente_id: UUID) -> bool:
    """Indica si hay un técnico con sesión de tracking GPS activa para el incidente."""
    return incidente_id in CONEXIONES_TECNICO


async def registrar_tecnico_tracking(incidente_id: UUID, websocket: WebSocket) -> None:
    """
    Registra la conexión de tracking del técnico. Si ya había una sesión activa
    (p. ej. una reconexión tras un corte de red), cierra la anterior y la nueva
    toma el control — evita que el técnico quede bloqueado por una sesión stale.
    """
    anterior = CONEXIONES_TECNICO.get(incidente_id)
    if anterior is not None and anterior is not websocket:
        try:
            await anterior.close(code=1000)
        except Exception:
            pass
    CONEXIONES_TECNICO[incidente_id] = websocket
    logger.info("Tracking GPS iniciado — incidente %s", incidente_id)


def desregistrar_tecnico_tracking(incidente_id: UUID, websocket: WebSocket | None = None) -> None:
    """
    Elimina la conexión de tracking del técnico al desconectarse.
    Solo borra si coincide con el socket dado (o si no se pasa ninguno), para no
    pisar una sesión nueva que ya tomó el control.
    """
    if websocket is None or CONEXIONES_TECNICO.get(incidente_id) is websocket:
        CONEXIONES_TECNICO.pop(incidente_id, None)
        logger.info("Tracking GPS finalizado — incidente %s", incidente_id)


async def cerrar_tracking_tecnico(incidente_id: UUID) -> None:
    """Cierra la sesión de tracking del técnico y notifica al canal del incidente."""
    ws = CONEXIONES_TECNICO.pop(incidente_id, None)
    if ws is None:
        return
    payload = {
        "tipo": "tracking_finalizado",
        "incidente_id": str(incidente_id),
        "mensaje": "El incidente fue atendido. La sesión de tracking GPS ha finalizado.",
        "timestamp": datetime.utcnow().isoformat(),
    }
    try:
        await ws.send_json(payload)
        await ws.close(code=1000)
    except Exception:
        logger.debug("Error cerrando WS de tracking para incidente %s", incidente_id)
    await broadcast_incidente_async(incidente_id, payload)


async def notificar_cancelacion_tecnico(incidente_id: UUID) -> None:
    """
    Avisa al técnico (canal de tracking + canal del incidente) que el cliente
    canceló el servicio, y cierra su sesión de tracking. La app del técnico
    muestra el aviso y queda libre.
    """
    payload = {
        "tipo": "servicio_cancelado",
        "incidente_id": str(incidente_id),
        "mensaje": "El servicio fue cancelado por el cliente.",
        "timestamp": datetime.utcnow().isoformat(),
    }
    ws = CONEXIONES_TECNICO.pop(incidente_id, None)
    if ws is not None:
        try:
            await ws.send_json(payload)
            await ws.close(code=1000)
        except Exception:
            logger.debug("Error cerrando WS de tracking (cancelación) para %s", incidente_id)
    await broadcast_incidente_async(incidente_id, payload)
