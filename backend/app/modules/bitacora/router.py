"""
Bitácora de auditoría (consulta). Solo TALLER (su tenant) y ADMIN (todo o por tenant).
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.users.models import USUARIOS
from app.modules.bitacora.models import BITACORA
from app.modules.bitacora.schemas import BitacoraResponse
from app.modules.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/bitacora", tags=["Bitácora"])

logger = logging.getLogger(__name__)


def _rol(usuario: USUARIOS) -> str:
    r = usuario.ROL
    return r.value if hasattr(r, "value") else str(r)


@router.get(
    "",
    response_model=list[BitacoraResponse],
    summary="Listar bitácora de auditoría",
    description=(
        "Registros de acciones de usuarios, filtrables. "
        "TALLER ve solo su tenant; ADMIN ve todo o filtra con `?id_tenant=`."
    ),
)
def listar_bitacora(
    accion: str | None = Query(None, description="Filtrar por acción"),
    entidad: str | None = Query(None, description="Filtrar por entidad"),
    id_usuario: int | None = Query(None, description="Filtrar por usuario"),
    id_tenant: int | None = Query(None, description="Filtrar por tenant (solo ADMIN)"),
    desde: datetime | None = Query(None, description="Fecha desde (ISO)"),
    hasta: datetime | None = Query(None, description="Fecha hasta (ISO)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    rol = _rol(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres y admins pueden ver la bitácora")

    # Resolver el tenant efectivo del filtro (TALLER siempre su tenant).
    if rol == "TALLER":
        tenant_efectivo = getattr(usuario, "_id_tenant", None) or usuario.ID_TENANT
    else:
        tenant_efectivo = id_tenant  # None = sin filtro (ADMIN ve todo)

    q = db.query(BITACORA, USUARIOS.NOMBRE_COMPLETO).outerjoin(
        USUARIOS, BITACORA.ID_USUARIO == USUARIOS.ID_USUARIO
    )
    if tenant_efectivo:
        q = q.filter(BITACORA.ID_TENANT == tenant_efectivo)
    if accion:
        q = q.filter(BITACORA.ACCION == accion)
    if entidad:
        q = q.filter(BITACORA.ENTIDAD == entidad)
    if id_usuario:
        q = q.filter(BITACORA.ID_USUARIO == id_usuario)
    if desde:
        q = q.filter(BITACORA.FECHA_CREACION >= desde)
    if hasta:
        q = q.filter(BITACORA.FECHA_CREACION <= hasta)

    filas = (
        q.order_by(BITACORA.FECHA_CREACION.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        BitacoraResponse(
            id_bitacora=b.ID_BITACORA,
            id_usuario=b.ID_USUARIO,
            usuario_nombre=nombre,
            id_tenant=b.ID_TENANT,
            accion=b.ACCION,
            entidad=b.ENTIDAD,
            id_entidad=b.ID_ENTIDAD,
            descripcion=b.DESCRIPCION,
            ip=b.IP,
            fecha_creacion=b.FECHA_CREACION,
        )
        for b, nombre in filas
    ]
