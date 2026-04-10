from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from app.core.config import settings


def verificar_contrasena(contrasena_plana: str, hash_contrasena: str) -> bool:
    return bcrypt.checkpw(
        contrasena_plana.encode("utf-8"),
        hash_contrasena.encode("utf-8"),
    )

def hashear_contrasena(contrasena: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(contrasena.encode("utf-8"), salt).decode("utf-8")

def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verificar_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Token inválido o expirado")