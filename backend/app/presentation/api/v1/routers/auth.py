from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import TALLERES, USUARIOS
from app.presentation.api.v1.schemas.auth import UserCreate, UserLogin, Token
from app.core.security import hashear_contrasena, verificar_contrasena, crear_access_token
from app.core.config import settings
from app.application.use_cases.tenant_service import TENANT_DEFAULT_ID

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(USUARIOS).filter(USUARIOS.CORREO_ELECTRONICO == user.correo_electronico).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = hashear_contrasena(user.contrasena)
    id_tenant_asignado = user.id_tenant or TENANT_DEFAULT_ID

    nuevo_usuario = USUARIOS(
        CORREO_ELECTRONICO=user.correo_electronico,
        HASH_CONTRASENA=hashed_password,
        NOMBRE_COMPLETO=user.nombre_completo,
        TELEFONO=user.telefono,
        ROL=user.rol,
        ID_TENANT=id_tenant_asignado,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Para rol TALLER: si ya existe un taller vinculado a este usuario, propagar id_tenant
    if user.rol == "TALLER":
        taller = db.query(TALLERES).filter(TALLERES.ID_USUARIO == nuevo_usuario.ID_USUARIO).first()
        if taller and taller.ID_TENANT is None:
            taller.ID_TENANT = id_tenant_asignado
            db.add(taller)
            db.commit()

    access_token = crear_access_token(
        data={
            "sub": nuevo_usuario.CORREO_ELECTRONICO,
            "rol": nuevo_usuario.ROL,
            "id_tenant": str(id_tenant_asignado),
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    usuario = db.query(USUARIOS).filter(USUARIOS.CORREO_ELECTRONICO == user.correo_electronico).first()
    if not usuario or not verificar_contrasena(user.contrasena, usuario.HASH_CONTRASENA):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    id_tenant = usuario.ID_TENANT or TENANT_DEFAULT_ID

    access_token = crear_access_token(
        data={
            "sub": usuario.CORREO_ELECTRONICO,
            "rol": usuario.ROL,
            "id_tenant": str(id_tenant),
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}