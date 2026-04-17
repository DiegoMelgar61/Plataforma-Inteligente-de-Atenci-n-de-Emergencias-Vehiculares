"""
Router de notificaciones y seguimiento en tiempo real (WebSocket).
Tags = ["Notificaciones y Tiempo Real"]
"""
import json
import logging
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import INCIDENTES, USUARIOS
from app.presentation.api.v1.dependencies.auth import get_current_user
from app.application.use_cases.notification_service import (
    registrar_conexion_websocket,
    desregistrar_conexion_websocket,
    broadcast_estado_actualizado,
    enviar_notificacion_cliente,
    registrar_conexion_global,
    desregistrar_conexion_global,
)

router = APIRouter(prefix="/notifications", tags=["Notificaciones y Tiempo Real"])

logger = logging.getLogger(__name__)


def _rol_texto(usuario: USUARIOS) -> str:
    """Obtiene el rol como string."""
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


@router.websocket("/ws")
async def websocket_global(websocket: WebSocket):
    """
    WebSocket global para Dashboard y Mapa.
    Recibe broadcasts de cualquier cambio de estado de incidentes.
    No requiere autenticación ni id de incidente.
    """
    await websocket.accept()
    registrar_conexion_global(websocket)
    try:
        await websocket.send_json({
            "tipo": "conectado",
            "mensaje": "Conectado al canal global",
            "timestamp": datetime.utcnow().isoformat(),
        })
        while True:
            await websocket.receive_text()  # mantener conexión viva
    except WebSocketDisconnect:
        desregistrar_conexion_global(websocket)
    except Exception:
        desregistrar_conexion_global(websocket)
        try:
            await websocket.close()
        except Exception:
            pass


@router.websocket("/ws/incidents/{id_incidente}")
async def websocket_seguimiento_incidente(
    websocket: WebSocket,
    id_incidente: UUID,
):
    """
    WebSocket para seguimiento en tiempo real del estado de un incidente.

    Clientes conectados reciben notificaciones cuando:
    - Cambia el estado del incidente
    - Se asigna a un taller
    - Se actualiza información relevante

    **Flujo:**
    1. Cliente se conecta a /ws/incidents/{id_incidente}
    2. Se registra la conexión
    3. Servidor envía eventos JSON con cambios de estado
    4. Mantiene conexión hasta que cliente se desconecta

    **Mensaje de ejemplo:**
    ```json
    {
        "tipo": "estado_actualizado",
        "incidente_id": "uuid",
        "nuevo_estado": "EN_CAMINO",
        "timestamp": "2026-04-05T12:00:00"
    }
    ```
    """
    await websocket.accept()

    try:
        # Registrar conexión
        registrar_conexion_websocket(id_incidente, websocket)
        logger.info("WebSocket conectado para incidente %s", id_incidente)

        # Enviar confirmación de conexión
        await websocket.send_json({
            "tipo": "conectado",
            "incidente_id": str(id_incidente),
            "mensaje": "Conectado a seguimiento en tiempo real",
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Mantener conexión abierta (escuchar mensajes del cliente si es necesario)
        while True:
            data = await websocket.receive_text()
            # Procesar mensajes del cliente si es necesario
            try:
                mensaje = json.loads(data)
                logger.debug(
                    "Mensaje recibido del cliente para incidente %s: %s",
                    id_incidente,
                    mensaje.get("tipo"),
                )
            except json.JSONDecodeError:
                logger.warning("Mensaje JSON inválido recibido")

    except WebSocketDisconnect:
        logger.info("WebSocket desconectado para incidente %s", id_incidente)
        desregistrar_conexion_websocket(id_incidente, websocket)
    except Exception as e:
        logger.exception("Error en WebSocket para incidente %s", id_incidente)
        desregistrar_conexion_websocket(id_incidente, websocket)
        try:
            await websocket.close(code=status.WS_1011_SERVER_ERROR)
        except Exception:
            pass


@router.post(
    "/test",
    status_code=status.HTTP_200_OK,
    summary="Test de notificación",
    description="Envía una notificación de prueba al incidente especificado (solo para desarrollo).",
    response_description="Notificación enviada exitosamente",
)
def enviar_notificacion_prueba(
    id_incidente: UUID,
    mensaje: str = "Mensaje de prueba",
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    """
    Endpoint para pruebas de notificaciones.

    Requiere autenticación. Envía una notificación de prueba a todos los WebSocket
    conectados para el incidente especificado.

    **Parámetros query:**
    - `id_incidente` (UUID): ID del incidente
    - `mensaje` (str, opcional): Mensaje personalizado. Default: "Mensaje de prueba"

    **Respuesta:**
    ```json
    {
        "exito": true,
        "incidente_id": "uuid",
        "mensaje_enviado": "Mensaje de prueba",
        "timestamp": "2026-04-05T12:00:00"
    }
    ```
    """
    # Verificar que el incidente existe
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # Para desarrollo, permitir ADMIN o el dueño del incidente
    rol = _rol_texto(usuario)
    es_propietario = incidente.ID_USUARIO_CLIENTE == usuario.ID_USUARIO
    es_admin = rol == "ADMIN"

    if not (es_propietario or es_admin):
        raise HTTPException(
            status_code=403,
            detail="No autorizado a enviar notificaciones para este incidente",
        )

    try:
        # Enviar notificación
        enviar_notificacion_cliente(db, id_incidente, mensaje)

        return {
            "exito": True,
            "incidente_id": str(id_incidente),
            "mensaje_enviado": mensaje,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.exception("Error al enviar notificación de prueba")
        raise HTTPException(
            status_code=500,
            detail="Error al enviar notificación",
        )


@router.post(
    "/incidents/{id_incidente}/update-status",
    status_code=status.HTTP_200_OK,
    summary="Actualizar estado e notificar",
    description="Actualiza el estado del incidente y notifica automáticamente.",
    response_description="Estado actualizado y notificaciones enviadas",
)
def actualizar_estado_incidente(
    id_incidente: UUID,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_user),
):
    """
    Actualiza el estado de un incidente y envía notificaciones automáticas
    al cliente y al taller (si está asignado).

    **Estados válidos:**
    - PENDIENTE, EN_PROCESO_IA, CLASIFICADO, ASIGNADO, EN_CAMINO, EN_PROCESO,
      ATENDIDO, CANCELADO, INCIERTO

    **Parámetros:**
    - `id_incidente` (UUID): ID del incidente
    - `nuevo_estado` (str): Nuevo estado

    **Respuesta:**
    ```json
    {
        "exito": true,
        "incidente_id": "uuid",
        "estado_anterior": "ASIGNADO",
        "estado_nuevo": "EN_CAMINO",
        "timestamp": "2026-04-05T12:00:00"
    }
    ```
    """
    # Verificar que el incidente existe
    incidente = db.query(INCIDENTES).filter(INCIDENTES.ID_INCIDENTE == id_incidente).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    # Autorización: ADMIN o dueño del incidente
    rol = _rol_texto(usuario)
    es_propietario = incidente.ID_USUARIO_CLIENTE == usuario.ID_USUARIO
    es_admin = rol == "ADMIN"

    # Los talleres también pueden actualizar si tienen asignación
    from app.models.models import ASIGNACIONES

    tiene_asignacion = (
        db.query(ASIGNACIONES)
        .filter(ASIGNACIONES.ID_INCIDENTE == id_incidente)
        .first()
    )
    es_taller_asignado = False
    if tiene_asignacion and rol == "TALLER":
        # Verificar si el usuario es el dueño del taller asignado
        from app.models.models import TALLERES

        taller = (
            db.query(TALLERES)
            .filter(TALLERES.ID_TALLER == tiene_asignacion.ID_TALLER)
            .first()
        )
        es_taller_asignado = taller and taller.ID_USUARIO == usuario.ID_USUARIO

    if not (es_propietario or es_admin or es_taller_asignado):
        raise HTTPException(
            status_code=403,
            detail="No autorizado a actualizar este incidente",
        )

    estado_anterior = (
        incidente.ESTADO.value if hasattr(incidente.ESTADO, "value")
        else str(incidente.ESTADO)
    )

    try:
        # Actualizar estado
        incidente.ESTADO = nuevo_estado
        db.add(incidente)
        db.commit()
        db.refresh(incidente)

        # Enviar notificaciones automáticas
        broadcast_estado_actualizado(db, id_incidente, nuevo_estado)

        return {
            "exito": True,
            "incidente_id": str(id_incidente),
            "estado_anterior": estado_anterior,
            "estado_nuevo": nuevo_estado,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.exception("Error al actualizar estado del incidente %s", id_incidente)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar estado",
        )
