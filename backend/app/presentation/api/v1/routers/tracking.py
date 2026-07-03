"""
WebSocket de tracking GPS en tiempo real para técnicos.

Flujo:
  1. Técnico se conecta: WS /tracking/ws/incidents/{id}?token=<jwt>
  2. Servidor valida token, rol TECNICO y asignación activa al incidente.
  3. Se acepta la conexión y se registra como sesión de tracking.
  4. Técnico envía JSON: {"lat": float, "lng": float}
  5. Servidor persiste UBICACION_ACTUAL en TECNICOS y hace broadcast al canal del incidente.
  6. Cliente/taller, suscritos a /notifications/ws/incidents/{id}, reciben en tiempo real.
  7. Al llegar a estado ATENDIDO el servidor cierra la sesión vía cerrar_tracking_tecnico().
"""
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select, update

from app.core.database import AsyncSessionLocal
from app.core.security import verificar_token
from app.models.models import ASIGNACIONES, INCIDENTES
from app.modules.technicians.models import TECNICOS
from app.modules.users.models import USUARIOS
from app.application.use_cases.notification_service import (
    broadcast_incidente_async,
    desregistrar_tecnico_tracking,
    registrar_tecnico_tracking,
)

router = APIRouter(prefix="/tracking", tags=["Tracking GPS"])

logger = logging.getLogger(__name__)


@router.websocket("/ws/incidents/{id_incidente}")
async def tracking_websocket(
    websocket: WebSocket,
    id_incidente: UUID,
    token: str = Query(..., description="JWT Bearer token del técnico"),
):
    """
    Canal WebSocket exclusivo del técnico para transmitir ubicación GPS en tiempo real.

    **Conexión:** `wss://<host>/tracking/ws/incidents/{id_incidente}?token=<jwt>`

    **Mensajes que envía el técnico (JSON):**
    ```json
    {"lat": -34.6037, "lng": -58.3816}
    ```

    **Mensajes que recibe el técnico:**
    - `tracking_iniciado` — confirmación de sesión activa
    - `tracking_finalizado` — incidente cerrado, conexión se cierra con código 1000
    - `error` — mensaje de validación

    **Mensajes que reciben los suscriptores del incidente** (`/notifications/ws/incidents/{id}`):
    ```json
    {
        "tipo": "ubicacion_tecnico",
        "incidente_id": "uuid",
        "tecnico_id": "uuid",
        "lat": -34.6037,
        "lng": -58.3816,
        "timestamp": "2026-06-04T12:00:00"
    }
    ```
    """
    # ── 1. Validar token ──────────────────────────────────────────────────────
    try:
        payload = verificar_token(token)
    except ValueError:
        await websocket.close(code=1008, reason="Token inválido o expirado")
        return

    correo = payload.get("sub")
    if not correo:
        await websocket.close(code=1008, reason="Token sin sujeto válido")
        return

    # ── 2. Validar técnico y asignación ───────────────────────────────────────
    tecnico_id: UUID | None = None
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(USUARIOS).where(USUARIOS.CORREO_ELECTRONICO == correo)
            )
            usuario = result.scalar_one_or_none()
            if not usuario:
                await websocket.close(code=1008, reason="Usuario no encontrado")
                return

            rol = usuario.ROL.value if hasattr(usuario.ROL, "value") else str(usuario.ROL)
            if rol != "TECNICO":
                await websocket.close(code=1008, reason="Solo técnicos pueden usar este canal")
                return

            result = await db.execute(
                select(TECNICOS).where(TECNICOS.ID_USUARIO == usuario.ID_USUARIO)
            )
            tecnico = result.scalar_one_or_none()
            if not tecnico:
                await websocket.close(code=1008, reason="Perfil de técnico no encontrado")
                return

            tecnico_id = tecnico.ID_TECNICO

            result = await db.execute(
                select(ASIGNACIONES).where(
                    ASIGNACIONES.ID_INCIDENTE == id_incidente,
                    ASIGNACIONES.ID_TECNICO == tecnico_id,
                    ASIGNACIONES.FECHA_RECHAZO.is_(None),
                )
            )
            if not result.scalar_one_or_none():
                await websocket.close(code=1008, reason="No estás asignado a este incidente")
                return

            result = await db.execute(
                select(INCIDENTES.ESTADO).where(INCIDENTES.ID_INCIDENTE == id_incidente)
            )
            row = result.first()
            if not row:
                await websocket.close(code=1008, reason="Incidente no encontrado")
                return

            estado_str = row[0].value if hasattr(row[0], "value") else str(row[0])
            if estado_str == "ATENDIDO":
                await websocket.close(code=1000, reason="El incidente ya fue atendido")
                return

    except Exception:
        logger.exception("Error validando tracking WS para incidente %s", id_incidente)
        await websocket.close(code=1011, reason="Error interno del servidor")
        return

    # ── 3. Aceptar y registrar (una reconexión toma el control de la anterior) ─
    await websocket.accept()
    await registrar_tecnico_tracking(id_incidente, websocket)

    logger.info("Tracking GPS activo — técnico %s, incidente %s", tecnico_id, id_incidente)

    try:
        await websocket.send_json({
            "tipo": "tracking_iniciado",
            "incidente_id": str(id_incidente),
            "tecnico_id": str(tecnico_id),
            "mensaje": "Sesión de tracking GPS activa. Enviá tu ubicación periódicamente.",
            "timestamp": datetime.utcnow().isoformat(),
        })

        # ── 5. Loop principal ─────────────────────────────────────────────────
        async with AsyncSessionLocal() as location_db:
            while True:
                try:
                    data = await websocket.receive_json()
                except WebSocketDisconnect:
                    break
                except ValueError:
                    await websocket.send_json({"error": "JSON inválido"})
                    continue

                try:
                    lat = float(data["lat"])
                    lng = float(data["lng"])
                except (KeyError, ValueError, TypeError):
                    await websocket.send_json(
                        {"error": "Formato inválido: se requieren lat y lng como números"}
                    )
                    continue

                if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                    await websocket.send_json({"error": "Coordenadas fuera de rango"})
                    continue

                # Persistir ubicación en TECNICOS.UBICACION_ACTUAL
                try:
                    stmt = (
                        update(TECNICOS)
                        .where(TECNICOS.ID_TECNICO == tecnico_id)
                        .values(
                            UBICACION_ACTUAL=func.ST_SetSRID(
                                func.ST_MakePoint(lng, lat), 4326
                            )
                        )
                    )
                    await location_db.execute(stmt)
                    await location_db.commit()
                except Exception:
                    logger.exception(
                        "Error persistiendo ubicación del técnico %s", tecnico_id
                    )

                # Broadcast a suscriptores del incidente (cliente + taller)
                await broadcast_incidente_async(
                    id_incidente,
                    {
                        "tipo": "ubicacion_tecnico",
                        "incidente_id": str(id_incidente),
                        "tecnico_id": str(tecnico_id),
                        "lat": lat,
                        "lng": lng,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("Error inesperado en tracking WS — incidente %s", id_incidente)
    finally:
        desregistrar_tecnico_tracking(id_incidente, websocket)
        logger.info("Tracking GPS cerrado — técnico %s, incidente %s", tecnico_id, id_incidente)
