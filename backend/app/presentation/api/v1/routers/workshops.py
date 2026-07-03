"""
CRUD de talleres: listado para usuarios autenticados; alta/edición por dueño (rol TALLER) o ADMIN.
"""
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import TALLERES, USUARIOS
from app.modules.auth.dependencies import (
    get_current_active_user,
)
from app.presentation.api.v1.schemas.workshop import (
    WorkshopCreate,
    WorkshopResponse,
    WorkshopUpdate,
)

router = APIRouter(prefix="/talleres", tags=["Talleres"])


def _rol_texto(u: USUARIOS) -> str:
    r = u.ROL
    return r.value if hasattr(r, "value") else str(r)


def _puede_gestionar_taller(db: Session, usuario: USUARIOS, taller: TALLERES) -> bool:
    if _rol_texto(usuario) == "ADMIN":
        return True
    if _rol_texto(usuario) == "TALLER" and taller.ID_USUARIO == usuario.ID_USUARIO:
        return True
    return False


@router.get("", response_model=list[WorkshopResponse])
def listar_talleres(
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """Listado de talleres (cualquier usuario autenticado). Por defecto solo activos."""
    q = db.query(TALLERES)
    if solo_activos:
        q = q.filter(TALLERES.ACTIVO.is_(True))
    if _rol_texto(usuario) != "ADMIN":
        id_tenant = getattr(usuario, "_id_tenant", None)
        if id_tenant is not None:
            q = q.filter(TALLERES.ID_TENANT == id_tenant)
    items = q.order_by(TALLERES.NOMBRE_NEGOCIO).all()
    return [WorkshopResponse.model_validate(t) for t in items]


@router.get("/{id_taller}", response_model=WorkshopResponse)
def obtener_taller(
    id_taller: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """Detalle de un taller. Los no-admin solo pueden ver talleres de su tenant."""
    t = db.query(TALLERES).filter(TALLERES.ID_TALLER == id_taller).first()
    if not t:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    if _rol_texto(usuario) != "ADMIN":
        id_tenant = getattr(usuario, "_id_tenant", None)
        if id_tenant is not None and t.ID_TENANT != id_tenant:
            raise HTTPException(status_code=403, detail="Taller de otra red de talleres")
    return WorkshopResponse.model_validate(t)


@router.post("", response_model=WorkshopResponse, status_code=status.HTTP_201_CREATED)
def crear_taller(
    datos: WorkshopCreate,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """
    Crea el registro de taller.
    - TALLER: crea su propio taller (máximo 1 por cuenta).
    - ADMIN: puede crear talleres sin vincularlos a una cuenta dueña.
    """
    rol = _rol_texto(usuario)
    if rol not in ("TALLER", "ADMIN"):
        raise HTTPException(status_code=403, detail="Solo talleres o admins pueden crear talleres")

    id_usuario_dueno = None
    if rol == "TALLER":
        existente = db.query(TALLERES).filter(TALLERES.ID_USUARIO == usuario.ID_USUARIO).first()
        if existente:
            raise HTTPException(status_code=400, detail="Este usuario ya tiene un taller registrado")
        id_usuario_dueno = usuario.ID_USUARIO

    if datos.nit:
        nit_ocupado = db.query(TALLERES).filter(TALLERES.NIT == datos.nit).first()
        if nit_ocupado:
            raise HTTPException(status_code=400, detail="El NIT ya está registrado")

    taller = TALLERES(
        ID_USUARIO=id_usuario_dueno,
        NOMBRE_NEGOCIO=datos.nombre_negocio,
        NIT=datos.nit,
        DIRECCION=datos.direccion,
        TASA_COMISION=datos.tasa_comision if datos.tasa_comision is not None else Decimal("10.00"),
        LATITUD=datos.latitud,
        LONGITUD=datos.longitud,
        ACTIVO=True,
        ID_TENANT=getattr(usuario, "_id_tenant", None),
    )
    db.add(taller)
    db.commit()
    db.refresh(taller)
    return WorkshopResponse.model_validate(taller)


@router.put("/{id_taller}", response_model=WorkshopResponse)
def actualizar_taller(
    id_taller: UUID,
    datos: WorkshopUpdate,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """Actualiza taller (dueño del mismo o ADMIN)."""
    t = db.query(TALLERES).filter(TALLERES.ID_TALLER == id_taller).first()
    if not t:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    if not _puede_gestionar_taller(db, usuario, t):
        raise HTTPException(status_code=403, detail="No autorizado a modificar este taller")

    if datos.nit is not None and datos.nit != t.NIT:
        nit_ocupado = (
            db.query(TALLERES)
            .filter(TALLERES.NIT == datos.nit, TALLERES.ID_TALLER != id_taller)
            .first()
        )
        if nit_ocupado:
            raise HTTPException(status_code=400, detail="El NIT ya está en uso")

    if datos.nombre_negocio is not None:
        t.NOMBRE_NEGOCIO = datos.nombre_negocio
    if datos.nit is not None:
        t.NIT = datos.nit
    if datos.direccion is not None:
        t.DIRECCION = datos.direccion
    if datos.tasa_comision is not None:
        t.TASA_COMISION = datos.tasa_comision
    if datos.latitud is not None:
        t.LATITUD = datos.latitud
    if datos.longitud is not None:
        t.LONGITUD = datos.longitud
    if datos.activo is not None:
        t.ACTIVO = datos.activo

    db.add(t)
    db.commit()
    db.refresh(t)
    return WorkshopResponse.model_validate(t)


@router.delete("/{id_taller}", status_code=status.HTTP_204_NO_CONTENT)
def baja_logica_taller(
    id_taller: UUID,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """Desactiva el taller (dueño o ADMIN); no borra filas."""
    t = db.query(TALLERES).filter(TALLERES.ID_TALLER == id_taller).first()
    if not t:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    if not _puede_gestionar_taller(db, usuario, t):
        raise HTTPException(status_code=403, detail="No autorizado a dar de baja este taller")
    t.ACTIVO = False
    db.add(t)
    db.commit()
    return None
