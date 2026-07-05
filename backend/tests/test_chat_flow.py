"""
Smoke tests del chat de IA por incidente.

Cobertura:
  - Mensaje del cliente en incidente ASIGNADO persiste y devuelve el
    fallback seguro cuando Gemini no está disponible.
  - Validación de estado: no se puede chatear en un incidente PENDIENTE.
  - El hilo del técnico se autocrea con el mensaje de apertura (sugerencia).

Estrategia: TestClient de FastAPI + SQLite en memoria (mismo patrón que
test_technician_flow.py). Los IDs son enteros autoincrementales — a
diferencia de test_technician_flow.py, NO se asignan UUIDs manualmente,
porque los modelos ya usan Integer como PK.

Para ejecutar:
    cd backend
    pytest tests/test_chat_flow.py -v
"""
from unittest.mock import patch

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── Parchear columnas PostGIS ANTES de importar los modelos ──────────────────
from geoalchemy2 import Geography as _Geography
_Geography.__init_subclass__ = classmethod(lambda cls, **kw: None)

from app.core.database import Base, get_db  # noqa: E402
from app.core.security import crear_access_token, hashear_contrasena  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.assignments.models import ASIGNACIONES  # noqa: E402
from app.modules.chat.models import CONVERSACIONES, MENSAJES_CHAT  # noqa: E402
from app.modules.incidents.models import INCIDENTES  # noqa: E402
from app.modules.technicians.models import TECNICOS  # noqa: E402
from app.modules.users.models import USUARIOS  # noqa: E402
from app.modules.workshops.models import TALLERES  # noqa: E402

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def _patch_geography_columns() -> None:
    for table in Base.metadata.tables.values():
        for col in table.columns:
            if type(col.type).__name__ == "Geography":
                col.type = sa.Text()


_patch_geography_columns()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Re-afirma el override en cada módulo: si test_technician_flow.py se
    # importa en la misma sesión de pytest, también pisa
    # app.dependency_overrides[get_db] (ambos módulos comparten el singleton
    # `app`) y gana el que se haya importado último. Sin esto, el orden de
    # recolección de pytest decide silenciosamente qué engine SQLite responde.
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# ─────────────────────── helpers de fixtures ─────────────────────────────────

def _make_user(db, correo: str, rol: str, nombre: str = "Test User") -> USUARIOS:
    u = USUARIOS(
        CORREO_ELECTRONICO=correo,
        HASH_CONTRASENA=hashear_contrasena("Segura123!"),
        NOMBRE_COMPLETO=nombre,
        ROL=rol,
        ACTIVO=True,
    )
    db.add(u)
    db.flush()
    return u


def _make_taller(db, usuario: USUARIOS) -> TALLERES:
    t = TALLERES(
        ID_USUARIO=usuario.ID_USUARIO,
        NOMBRE_NEGOCIO="Taller Test",
        NIT=f"NIT-{usuario.ID_USUARIO}",
    )
    db.add(t)
    db.flush()
    return t


def _make_tecnico(db, taller: TALLERES, usuario: USUARIOS) -> TECNICOS:
    t = TECNICOS(
        ID_TALLER=taller.ID_TALLER,
        ID_USUARIO=usuario.ID_USUARIO,
        NOMBRE_COMPLETO=usuario.NOMBRE_COMPLETO,
        DISPONIBLE=True,
    )
    db.add(t)
    db.flush()
    return t


def _make_incidente(db, cliente: USUARIOS, estado: str = "ASIGNADO") -> INCIDENTES:
    # ID_TENANT=1 replica el tenant por defecto (TENANT_DEFAULT_ID) que
    # get_current_user asigna a TALLER/TECNICO vía usuario._id_tenant.
    inc = INCIDENTES(
        ID_USUARIO_CLIENTE=cliente.ID_USUARIO,
        UBICACION="POINT(-68.15 -16.50)",
        ESTADO=estado,
        PRIORIDAD="MEDIA",
        CLASIFICACION="OTROS",
        ID_TENANT=1,
    )
    db.add(inc)
    db.flush()
    return inc


def _make_asignacion(db, incidente: INCIDENTES, taller: TALLERES, tecnico: TECNICOS) -> ASIGNACIONES:
    a = ASIGNACIONES(
        ID_INCIDENTE=incidente.ID_INCIDENTE,
        ID_TALLER=taller.ID_TALLER,
        ID_TECNICO=tecnico.ID_TECNICO,
    )
    db.add(a)
    db.flush()
    return a


def _auth_headers(usuario: USUARIOS) -> dict:
    token = crear_access_token({"sub": usuario.CORREO_ELECTRONICO, "rol": usuario.ROL})
    return {"Authorization": f"Bearer {token}"}


# ═════════════════════════════════════════════════════════════════════════════
# TEST 1 — Mensaje del cliente + fallback de IA
# ═════════════════════════════════════════════════════════════════════════════

class TestChatCliente:

    def test_mensaje_cliente_persiste_y_usa_fallback_si_ia_falla(self, client, db):
        u_cli = _make_user(db, "cli_chat1@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="ASIGNADO")
        db.commit()

        with patch(
            "app.modules.chat.service.run_gemini",
            side_effect=RuntimeError("Gemini no disponible"),
        ):
            resp = client.post(
                f"/chat/incidents/{inc.ID_INCIDENTE}/cliente/mensajes",
                data={"contenido": "Se me pinchó una llanta en la autopista"},
                headers=_auth_headers(u_cli),
            )

        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["mensaje_usuario"]["contenido"] == "Se me pinchó una llanta en la autopista"
        assert data["mensaje_usuario"]["rol_emisor"] == "CLIENTE"
        assert data["mensaje_ia"]["rol_emisor"] == "IA"
        assert "no puedo procesar tu mensaje" in data["mensaje_ia"]["contenido"]

        mensajes = (
            db.query(MENSAJES_CHAT)
            .join(CONVERSACIONES, MENSAJES_CHAT.ID_CONVERSACION == CONVERSACIONES.ID_CONVERSACION)
            .filter(CONVERSACIONES.ID_INCIDENTE == inc.ID_INCIDENTE)
            .all()
        )
        assert len(mensajes) == 2

    def test_mensaje_vacio_sin_adjunto_retorna_422(self, client, db):
        u_cli = _make_user(db, "cli_chat2@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="ASIGNADO")
        db.commit()

        resp = client.post(
            f"/chat/incidents/{inc.ID_INCIDENTE}/cliente/mensajes",
            data={},
            headers=_auth_headers(u_cli),
        )
        assert resp.status_code == 422

    def test_chat_rechazado_en_incidente_pendiente(self, client, db):
        u_cli = _make_user(db, "cli_chat3@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="PENDIENTE")
        db.commit()

        resp = client.post(
            f"/chat/incidents/{inc.ID_INCIDENTE}/cliente/mensajes",
            data={"contenido": "Hola, necesito ayuda"},
            headers=_auth_headers(u_cli),
        )
        assert resp.status_code == 409
        assert "no está disponible" in resp.json()["detail"]

    def test_otro_cliente_no_puede_chatear_en_incidente_ajeno(self, client, db):
        u_cli = _make_user(db, "cli_chat4a@test.com", "CLIENTE")
        u_otro = _make_user(db, "cli_chat4b@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="ASIGNADO")
        db.commit()

        resp = client.post(
            f"/chat/incidents/{inc.ID_INCIDENTE}/cliente/mensajes",
            data={"contenido": "Intento ajeno"},
            headers=_auth_headers(u_otro),
        )
        assert resp.status_code == 403


# ═════════════════════════════════════════════════════════════════════════════
# TEST 2 — Copiloto del técnico: autocreación con sugerencia de apertura
# ═════════════════════════════════════════════════════════════════════════════

class TestChatTecnico:

    def test_hilo_tecnico_autocrea_con_sugerencia_apertura(self, client, db):
        u_t = _make_user(db, "taller_chat1@test.com", "TALLER")
        taller = _make_taller(db, u_t)
        u_tec = _make_user(db, "tec_chat1@test.com", "TECNICO")
        tec = _make_tecnico(db, taller, u_tec)
        u_cli = _make_user(db, "cli_chat5@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="ASIGNADO")
        _make_asignacion(db, inc, taller, tec)
        db.commit()

        with patch(
            "app.modules.chat.service.run_gemini",
            return_value={"respuesta": "Llevá gato hidráulico y llave de cruz."},
        ):
            resp = client.get(
                f"/chat/incidents/{inc.ID_INCIDENTE}/tecnico/mensajes",
                headers=_auth_headers(u_tec),
            )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["tipo"] == "TECNICO"
        assert len(data["mensajes"]) == 1
        assert data["mensajes"][0]["rol_emisor"] == "IA"
        assert "gato hidráulico" in data["mensajes"][0]["contenido"]

    def test_tecnico_no_asignado_no_puede_ver_copiloto(self, client, db):
        u_t = _make_user(db, "taller_chat2@test.com", "TALLER")
        taller = _make_taller(db, u_t)
        u_tec_asignado = _make_user(db, "tec_chat2a@test.com", "TECNICO")
        tec_asignado = _make_tecnico(db, taller, u_tec_asignado)
        u_tec_otro = _make_user(db, "tec_chat2b@test.com", "TECNICO")
        _make_tecnico(db, taller, u_tec_otro)
        u_cli = _make_user(db, "cli_chat6@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="ASIGNADO")
        _make_asignacion(db, inc, taller, tec_asignado)
        db.commit()

        resp = client.get(
            f"/chat/incidents/{inc.ID_INCIDENTE}/tecnico/mensajes",
            headers=_auth_headers(u_tec_otro),
        )
        assert resp.status_code == 403
