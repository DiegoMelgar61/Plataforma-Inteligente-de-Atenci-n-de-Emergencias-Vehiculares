from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import USUARIOS
from app.presentation.api.v1.schemas.auth import UserCreate, UserLogin, Token
from app.core.security import hashear_contrasena, verificar_contrasena, crear_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    usuario_existente = db.query(USUARIOS).filter(USUARIOS.CORREO_ELECTRONICO == user.correo_electronico).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Crear usuario
    hashed_password = hashear_contrasena(user.contrasena)
    nuevo_usuario = USUARIOS(
        CORREO_ELECTRONICO=user.correo_electronico,
        HASH_CONTRASENA=hashed_password,
        NOMBRE_COMPLETO=user.nombre_completo,
        TELEFONO=user.telefono,
        ROL=user.rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Generar token
    access_token = crear_access_token(
        data={"sub": nuevo_usuario.CORREO_ELECTRONICO, "rol": nuevo_usuario.ROL}
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

    access_token = crear_access_token(
        data={"sub": usuario.CORREO_ELECTRONICO, "rol": usuario.ROL}
    )
    return {"access_token": access_token, "token_type": "bearer"}