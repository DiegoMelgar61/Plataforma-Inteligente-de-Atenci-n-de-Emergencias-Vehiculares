from uuid import UUID

from pydantic import BaseModel, EmailStr
from typing import Literal

class UserCreate(BaseModel):
    correo_electronico: EmailStr
    contrasena: str
    nombre_completo: str
    telefono: str | None = None
    rol: Literal["CLIENTE", "TALLER", "ADMIN", "TECNICO"] = "CLIENTE"
    id_tenant: UUID | None = None

class UserLogin(BaseModel):
    correo_electronico: EmailStr
    contrasena: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    correo_electronico: str | None = None
    rol: str | None = None