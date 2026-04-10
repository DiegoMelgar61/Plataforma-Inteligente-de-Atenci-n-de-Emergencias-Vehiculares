"""
Perfil del usuario autenticado + gestión de usuarios (ADMIN).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import USUARIOS
from app.presentation.api.v1.dependencies.auth import get_current_active_user
from app.presentation.api.v1.schemas.user import UserProfile, UserUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _rol_texto(u: USUARIOS) -> str:
    r = u.ROL
    return r.value if hasattr(r, "value") else str(r)


def _solo_admin(usuario: USUARIOS) -> None:
    if _rol_texto(usuario) != "ADMIN":
        raise HTTPException(status_code=403, detail="Solo administradores pueden realizar esta acción")


@router.get("/me", response_model=UserProfile)
def obtener_mi_perfil(
    usuario: USUARIOS = Depends(get_current_active_user),
):
    return UserProfile.model_validate(usuario)


@router.put("/me", response_model=UserProfile)
def actualizar_mi_perfil(
    datos: UserUpdate,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    if datos.nombre_completo is not None:
        usuario.NOMBRE_COMPLETO = datos.nombre_completo
    if datos.telefono is not None:
        usuario.TELEFONO = datos.telefono
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return UserProfile.model_validate(usuario)


@router.get("", response_model=list[UserProfile])
def listar_usuarios(
    rol: str | None = None,
    activo: bool | None = None,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    _solo_admin(usuario)
    q = db.query(USUARIOS)
    if rol:
        q = q.filter(USUARIOS.ROL == rol)
    if activo is not None:
        q = q.filter(USUARIOS.ACTIVO == activo)
    return [UserProfile.model_validate(u) for u in q.order_by(USUARIOS.FECHA_CREACION.desc()).all()]


@router.patch("/{id_usuario}/rol")
def cambiar_rol(
    id_usuario: UUID,
    body: dict,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    _solo_admin(usuario)
    u = db.query(USUARIOS).filter(USUARIOS.ID_USUARIO == id_usuario).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    nuevo_rol = body.get("rol")
    if nuevo_rol not in ("CLIENTE", "TALLER", "ADMIN"):
        raise HTTPException(status_code=400, detail="Rol inválido")
    u.ROL = nuevo_rol
    db.commit()
    db.refresh(u)
    return UserProfile.model_validate(u)


@router.patch("/{id_usuario}/activo")
def cambiar_activo(
    id_usuario: UUID,
    body: dict,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    _solo_admin(usuario)
    u = db.query(USUARIOS).filter(USUARIOS.ID_USUARIO == id_usuario).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    u.ACTIVO = body.get("activo", True)
    db.commit()
    db.refresh(u)
    return UserProfile.model_validate(u)
