"""
Dependencias de autenticación y autorización por rol (JWT Bearer).
"""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verificar_token
from app.models.models import TECNICOS, USUARIOS

# Debe coincidir con la ruta real del login (router auth: prefix /auth + /login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _rol_como_texto(rol) -> str:
    """Normaliza el rol ORM (enum nativo o string) a texto."""
    if rol is None:
        return ""
    return rol.value if hasattr(rol, "value") else str(rol)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> USUARIOS:
    """
    Decodifica el JWT y devuelve el usuario persistido por correo (claim ``sub``).
    """
    try:
        payload = verificar_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    correo = payload.get("sub")
    if not correo or not isinstance(correo, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin sujeto válido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = db.query(USUARIOS).filter(USUARIOS.CORREO_ELECTRONICO == correo).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Inyectar id_tenant efectivo desde el token (con fallback al valor en DB o al default)
    from app.application.use_cases.tenant_service import TENANT_DEFAULT_ID
    id_tenant_str = payload.get("id_tenant")
    if id_tenant_str:
        try:
            usuario._id_tenant = UUID(str(id_tenant_str))
        except (ValueError, TypeError):
            usuario._id_tenant = TENANT_DEFAULT_ID
    else:
        usuario._id_tenant = usuario.ID_TENANT or TENANT_DEFAULT_ID

    return usuario


def get_current_active_user(
    usuario: USUARIOS = Depends(get_current_user),
) -> USUARIOS:
    """Usuario autenticado, activo y no eliminado lógicamente."""
    if not usuario.ACTIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    if usuario.FECHA_ELIMINACION is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario dado de baja",
        )
    return usuario


def get_current_cliente(
    usuario: USUARIOS = Depends(get_current_active_user),
) -> USUARIOS:
    """Solo cuentas con rol CLIENTE."""
    if _rol_como_texto(usuario.ROL) != "CLIENTE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación solo está disponible para clientes",
        )
    return usuario


def get_current_taller(
    usuario: USUARIOS = Depends(get_current_active_user),
) -> USUARIOS:
    """Solo cuentas con rol TALLER (dueño de negocio)."""
    if _rol_como_texto(usuario.ROL) != "TALLER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación solo está disponible para talleres",
        )
    return usuario


def get_current_admin(
    usuario: USUARIOS = Depends(get_current_active_user),
) -> USUARIOS:
    """Solo administradores de plataforma."""
    if _rol_como_texto(usuario.ROL) != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return usuario


def get_current_tecnico_usuario(
    usuario: USUARIOS = Depends(get_current_active_user),
) -> USUARIOS:
    """Solo cuentas con rol TECNICO (devuelve el USUARIOS ORM)."""
    if _rol_como_texto(usuario.ROL) != "TECNICO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación solo está disponible para técnicos",
        )
    return usuario


def get_current_tecnico(
    usuario: USUARIOS = Depends(get_current_tecnico_usuario),
    db: Session = Depends(get_db),
) -> TECNICOS:
    """
    Resuelve el registro TECNICOS del usuario con rol TECNICO.
    Lanza 404 si el usuario tiene el rol pero no tiene perfil de técnico creado.
    """
    tecnico = (
        db.query(TECNICOS)
        .filter(TECNICOS.ID_USUARIO == usuario.ID_USUARIO)
        .first()
    )
    if tecnico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de técnico no encontrado para este usuario",
        )
    return tecnico
