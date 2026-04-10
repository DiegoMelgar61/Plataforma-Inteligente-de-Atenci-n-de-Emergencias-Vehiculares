from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Siempre cargar backend/.env aunque ejecutes python desde la raíz del monorepo
_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_NAME: str = "Plataforma Inteligente de Atención de Emergencias Vehiculares"
    ENVIRONMENT: Literal["development", "production"] = "development"
    
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "emergencias_vehiculares"

    # Opcional: p. ej. "require" | "prefer" | "disable" (psycopg2). Si vacío, se infiere para supabase.co.
    POSTGRES_SSLMODE: str | None = None
    POSTGRES_REQUIRE_SSL: bool = False

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días

    # Almacenamiento local de evidencias (imágenes / audio)
    UPLOADS_DIR: Path = _BACKEND_DIR / "uploads"
    """Directorio raíz donde se guardan archivos subidos (se crea al arrancar)."""
    EVIDENCIAS_URL_PREFIX: str = "/static/evidencias"
    """Prefijo URL público para servir archivos vía StaticFiles en main."""

settings = Settings()