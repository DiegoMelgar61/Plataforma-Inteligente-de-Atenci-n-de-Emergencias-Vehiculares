"""
Perfil del usuario autenticado (cualquier rol activo).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import USUARIOS
from app.presentation.api.v1.dependencies.auth import get_current_active_user
from app.presentation.api.v1.schemas.user import UserProfile, UserUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=UserProfile)
def obtener_mi_perfil(
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """Devuelve los datos públicos del usuario del token."""
    return UserProfile.model_validate(usuario)


@router.put("/me", response_model=UserProfile)
def actualizar_mi_perfil(
    datos: UserUpdate,
    db: Session = Depends(get_db),
    usuario: USUARIOS = Depends(get_current_active_user),
):
    """Actualiza nombre y teléfono del perfil propio."""
    if datos.nombre_completo is not None:
        usuario.NOMBRE_COMPLETO = datos.nombre_completo
    if datos.telefono is not None:
        usuario.TELEFONO = datos.telefono

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return UserProfile.model_validate(usuario)
