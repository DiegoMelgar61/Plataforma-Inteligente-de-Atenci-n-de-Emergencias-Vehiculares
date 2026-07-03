"""
Bitácora de auditoría: registro de acciones relevantes de los usuarios.

El registro usa una sesión propia y nunca lanza excepción, para que un fallo
de auditoría jamás interrumpa la acción principal. `id_entidad` se guarda como
texto (sin FK) para no atarse a la transacción de negocio.
"""
from __future__ import annotations

import logging

from app.core.database import SessionLocal
from app.modules.users.models import USUARIOS
from app.modules.bitacora.models import BITACORA

logger = logging.getLogger(__name__)


def registrar(
    accion: str,
    descripcion: str | None = None,
    *,
    usuario: USUARIOS | None = None,
    id_usuario=None,
    id_tenant=None,
    entidad: str | None = None,
    id_entidad=None,
    ip: str | None = None,
) -> None:
    """Registra una entrada de bitácora. Best-effort: no propaga errores."""
    try:
        if usuario is not None:
            id_usuario = id_usuario or getattr(usuario, "ID_USUARIO", None)
            id_tenant = id_tenant or getattr(usuario, "_id_tenant", None) or getattr(
                usuario, "ID_TENANT", None
            )

        db = SessionLocal()
        try:
            entrada = BITACORA(
                ID_USUARIO=id_usuario,
                ID_TENANT=id_tenant,
                ACCION=accion,
                ENTIDAD=entidad,
                ID_ENTIDAD=str(id_entidad) if id_entidad is not None else None,
                DESCRIPCION=descripcion,
                IP=ip,
            )
            db.add(entrada)
            db.commit()
        finally:
            db.close()
    except Exception:
        logger.exception("No se pudo registrar en bitácora: accion=%s", accion)
