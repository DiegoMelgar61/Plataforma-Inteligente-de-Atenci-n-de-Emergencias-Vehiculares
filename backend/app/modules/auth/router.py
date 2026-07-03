from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.users.models import USUARIOS
from app.modules.auth.schemas import UserCreate, UserLogin, Token
from app.core.security import hashear_contrasena, verificar_contrasena, crear_access_token
from app.modules.bitacora import service as bitacora_service
from app.modules.tenants.service import TENANT_DEFAULT_ID


def _ip(request: Request | None) -> str | None:
    return request.client.host if request and request.client else None

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(USUARIOS).filter(USUARIOS.CORREO_ELECTRONICO == user.correo_electronico).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = hashear_contrasena(user.contrasena)
    id_tenant_asignado = TENANT_DEFAULT_ID

    nuevo_usuario = USUARIOS(
        CORREO_ELECTRONICO=user.correo_electronico,
        HASH_CONTRASENA=hashed_password,
        NOMBRE_COMPLETO=user.nombre_completo,
        TELEFONO=user.telefono,
        ROL="CLIENTE",
        ID_TENANT=id_tenant_asignado,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    access_token = crear_access_token(
        data={
            "sub": nuevo_usuario.CORREO_ELECTRONICO,
            "rol": nuevo_usuario.ROL,
            "id_tenant": str(id_tenant_asignado),
        }
    )

    rol_txt = nuevo_usuario.ROL.value if hasattr(nuevo_usuario.ROL, "value") else str(nuevo_usuario.ROL)
    bitacora_service.registrar(
        "USUARIO_REGISTRADO",
        f"Registro de {nuevo_usuario.CORREO_ELECTRONICO} (rol {rol_txt})",
        id_usuario=nuevo_usuario.ID_USUARIO,
        id_tenant=id_tenant_asignado,
        entidad="USUARIO",
        id_entidad=nuevo_usuario.ID_USUARIO,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, request: Request = None, db: Session = Depends(get_db)):
    usuario = db.query(USUARIOS).filter(USUARIOS.CORREO_ELECTRONICO == user.correo_electronico).first()
    if not usuario or not verificar_contrasena(user.contrasena, usuario.HASH_CONTRASENA):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.ACTIVO or usuario.FECHA_ELIMINACION is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")

    id_tenant = usuario.ID_TENANT or TENANT_DEFAULT_ID

    access_token = crear_access_token(
        data={
            "sub": usuario.CORREO_ELECTRONICO,
            "rol": usuario.ROL,
            "id_tenant": str(id_tenant),
        }
    )

    bitacora_service.registrar(
        "LOGIN",
        f"Inicio de sesión de {usuario.CORREO_ELECTRONICO}",
        id_usuario=usuario.ID_USUARIO,
        id_tenant=id_tenant,
        entidad="USUARIO",
        id_entidad=usuario.ID_USUARIO,
        ip=_ip(request),
    )
    return {"access_token": access_token, "token_type": "bearer"}
