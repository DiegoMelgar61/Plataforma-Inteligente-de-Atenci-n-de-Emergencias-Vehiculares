from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    correo_electronico: EmailStr
    contrasena: str
    nombre_completo: str
    telefono: str | None = None

class UserLogin(BaseModel):
    correo_electronico: EmailStr
    contrasena: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    correo_electronico: str | None = None
    rol: str | None = None
