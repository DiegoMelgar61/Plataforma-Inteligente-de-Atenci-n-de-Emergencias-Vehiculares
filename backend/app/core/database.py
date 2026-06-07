import ssl
from urllib.parse import quote_plus
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


def _pg_connect_args() -> dict:
    """Supabase y otros hosts en la nube suelen requerir TLS."""
    if settings.POSTGRES_SSLMODE:
        return {"sslmode": settings.POSTGRES_SSLMODE}
    host = (settings.POSTGRES_HOST or "").lower()
    if "supabase.co" in host or settings.POSTGRES_REQUIRE_SSL:
        return {"sslmode": "require"}
    return {}


def build_postgresql_url() -> str:
    """URL segura ante caracteres especiales en usuario/contraseña."""
    user = quote_plus(settings.POSTGRES_USER)
    password = quote_plus(settings.POSTGRES_PASSWORD)
    return (
        f"postgresql://{user}:{password}@{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


PSYCOPG2_CONNECT_ARGS: dict = _pg_connect_args()
DATABASE_URL: str = build_postgresql_url()

# Engine síncrono (endpoints síncronos, Alembic)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.ENVIRONMENT == "development",
    connect_args=PSYCOPG2_CONNECT_ARGS,
)

def _asyncpg_ssl_context() -> ssl.SSLContext:
    """
    SSL para asyncpg equivalente a psycopg2 `sslmode=require`: encripta la
    conexión pero NO verifica el certificado. Supabase presenta una cadena de
    certificados self-signed que `ssl=True` (verificación por defecto de asyncpg)
    rechaza con CERTIFICATE_VERIFY_FAILED, lo que rompía el WebSocket de tracking.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


_async_connect: dict = {
    # Supabase enruta por pgbouncer (modo transacción), que NO soporta prepared
    # statements persistentes. asyncpg los usa por defecto y rompe con
    # DuplicatePreparedStatementError. Hay que: (1) desactivar los cachés y
    # (2) darle un nombre ÚNICO a cada prepared statement, porque el pooler
    # reusa conexiones backend y los nombres fijos (__asyncpg_stmt_N__) chocan.
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
}
if PSYCOPG2_CONNECT_ARGS.get("sslmode") == "require":
    _async_connect["ssl"] = _asyncpg_ssl_context()
elif PSYCOPG2_CONNECT_ARGS.get("sslmode") == "disable":
    _async_connect["ssl"] = False

async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=_async_connect,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


def get_db():
    """Dependencia FastAPI: sesión síncrona (commit explícito en la ruta)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Sesión async; en rutas que mutan datos usa await db.commit() explícito."""
    async with AsyncSessionLocal() as db:
        yield db


def test_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Conexion a la base de datos: OK")
        return True
    except Exception as e:
        print(f"Error de conexion: {e}")
        return False
