"""
Tests del flujo de técnico: login, asignación activa y máquina de estados.

Cobertura:
  - Login de técnico (credenciales correctas e incorrectas)
  - Autorización: técnico no asignado no puede cambiar estado
  - Transiciones válidas: ASIGNADO→EN_CAMINO→EN_PROCESO→ATENDIDO
  - Transiciones inválidas reciben 400
  - Al pasar a ATENDIDO: técnico.disponible = True
  - Creación de técnico con cuenta de login (TALLER)

Estrategia: TestClient de FastAPI + SQLite en memoria.
Las columnas Geography (PostGIS) se reemplazan por Text antes de create_all.

Para ejecutar:
    cd backend
    pytest tests/test_technician_flow.py -v
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── Parchear columnas PostGIS ANTES de importar los modelos ──────────────────
# geoalchemy2.Geography no existe en SQLite; lo reemplazamos con Text.
from geoalchemy2 import Geography as _Geography
_Geography.__init_subclass__ = classmethod(lambda cls, **kw: None)

from app.core.database import Base, get_db  # noqa: E402
from app.core.security import crear_access_token, hashear_contrasena  # noqa: E402
from app.main import app  # noqa: E402
from app.models.models import (  # noqa: E402
    ASIGNACIONES,
    HISTORIAL_INCIDENTES,
    INCIDENTES,
    TALLERES,
    TECNICOS,
)
from app.modules.users.models import USUARIOS  # noqa: E402

# ─────────────────────── SQLite engine ───────────────────────────────────────

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# StaticPool garantiza que todas las sesiones comparten la MISMA conexión
# en-memoria; sin él cada conexión nueva crea una base de datos vacía.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def _patch_geography_columns() -> None:
    """Reemplaza columnas Geography por Text para compatibilidad con SQLite."""
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

def _uid() -> uuid.UUID:
    return uuid.uuid4()


def _make_user(db, correo: str, rol: str, nombre: str = "Test User") -> USUARIOS:
    u = USUARIOS(
        ID_USUARIO=_uid(),
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
        ID_TALLER=_uid(),
        ID_USUARIO=usuario.ID_USUARIO,
        NOMBRE_NEGOCIO="Taller Test",
        NIT=str(uuid.uuid4().int)[:8],
    )
    db.add(t)
    db.flush()
    return t


def _make_tecnico(db, taller: TALLERES, usuario: USUARIOS) -> TECNICOS:
    t = TECNICOS(
        ID_TECNICO=_uid(),
        ID_TALLER=taller.ID_TALLER,
        ID_USUARIO=usuario.ID_USUARIO,
        NOMBRE_COMPLETO=usuario.NOMBRE_COMPLETO,
        DISPONIBLE=True,
    )
    db.add(t)
    db.flush()
    return t


def _make_incidente(db, cliente: USUARIOS, estado: str = "ASIGNADO") -> INCIDENTES:
    # Geography se parchea a Text para SQLite; WKT como placeholder válido.
    inc = INCIDENTES(
        ID_INCIDENTE=_uid(),
        ID_USUARIO_CLIENTE=cliente.ID_USUARIO,
        UBICACION="POINT(-68.15 -16.50)",
        ESTADO=estado,
        PRIORIDAD="MEDIA",
        CLASIFICACION="OTROS",
    )
    db.add(inc)
    db.flush()
    return inc


def _make_asignacion(db, incidente: INCIDENTES, taller: TALLERES, tecnico: TECNICOS) -> ASIGNACIONES:
    a = ASIGNACIONES(
        ID_ASIGNACION=_uid(),
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
# TEST 1 — Login de técnico
# ═════════════════════════════════════════════════════════════════════════════

class TestLoginTecnico:

    def test_login_correcto_retorna_token(self, client, db):
        u = _make_user(db, "tecnico_l1@test.com", "TECNICO", "Juan Técnico")
        db.commit()

        resp = client.post("/auth/login", json={
            "correo_electronico": "tecnico_l1@test.com",
            "contrasena": "Segura123!",
        })
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_contrasena_incorrecta_401(self, client, db):
        _make_user(db, "tecnico_l2@test.com", "TECNICO")
        db.commit()

        resp = client.post("/auth/login", json={
            "correo_electronico": "tecnico_l2@test.com",
            "contrasena": "Incorrecta999",
        })
        assert resp.status_code == 401

    def test_perfil_me_devuelve_rol_tecnico(self, client, db):
        u = _make_user(db, "tecnico_l3@test.com", "TECNICO", "María Técnica")
        db.commit()

        resp = client.get("/usuarios/me", headers=_auth_headers(u))
        assert resp.status_code == 200
        assert resp.json()["rol"] == "TECNICO"


# ═════════════════════════════════════════════════════════════════════════════
# TEST 2 — GET /tecnicos/mi-asignacion
# ═════════════════════════════════════════════════════════════════════════════

class TestMiAsignacion:

    def test_tecnico_libre_retorna_null(self, client, db):
        u_t = _make_user(db, "taller_ma1@test.com", "TALLER")
        taller = _make_taller(db, u_t)
        u_tec = _make_user(db, "tec_ma1@test.com", "TECNICO")
        _make_tecnico(db, taller, u_tec)
        db.commit()

        resp = client.get("/tecnicos/mi-asignacion", headers=_auth_headers(u_tec))
        assert resp.status_code == 200
        assert resp.json() is None

    def test_tecnico_con_asignacion_activa(self, client, db):
        u_t = _make_user(db, "taller_ma2@test.com", "TALLER")
        taller = _make_taller(db, u_t)
        u_tec = _make_user(db, "tec_ma2@test.com", "TECNICO")
        tec = _make_tecnico(db, taller, u_tec)
        u_cli = _make_user(db, "cli_ma2@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="ASIGNADO")
        _make_asignacion(db, inc, taller, tec)
        db.commit()

        resp = client.get("/tecnicos/mi-asignacion", headers=_auth_headers(u_tec))
        assert resp.status_code == 200
        data = resp.json()
        assert data is not None
        assert data["estado_incidente"] == "ASIGNADO"
        assert data["id_tecnico"] == str(tec.ID_TECNICO)

    def test_cliente_no_puede_acceder_a_mi_asignacion(self, client, db):
        u_cli = _make_user(db, "cli_noma@test.com", "CLIENTE")
        db.commit()

        resp = client.get("/tecnicos/mi-asignacion", headers=_auth_headers(u_cli))
        assert resp.status_code == 403


# ═════════════════════════════════════════════════════════════════════════════
# TEST 3 — PATCH /tecnicos/incidente/{id}/estado (máquina de estados)
# ═════════════════════════════════════════════════════════════════════════════

class TestMaquinaEstados:

    def _setup(self, db, sufijo: str, estado: str = "ASIGNADO"):
        u_t = _make_user(db, f"taller_{sufijo}@t.com", "TALLER")
        taller = _make_taller(db, u_t)
        u_tec = _make_user(db, f"tech_{sufijo}@t.com", "TECNICO")
        tec = _make_tecnico(db, taller, u_tec)
        u_cli = _make_user(db, f"cli_{sufijo}@t.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado=estado)
        asig = _make_asignacion(db, inc, taller, tec)
        db.commit()
        return u_tec, tec, inc, asig

    def test_asignado_a_en_camino(self, client, db):
        u_tec, _, inc, _ = self._setup(db, "t1", "ASIGNADO")
        url = f"/tecnicos/incidente/{inc.ID_INCIDENTE}/estado"
        resp = client.patch(url, json={"nuevo_estado": "EN_CAMINO"}, headers=_auth_headers(u_tec))
        assert resp.status_code == 200, resp.text
        assert resp.json()["estado"] == "EN_CAMINO"

    def test_en_camino_a_en_proceso(self, client, db):
        u_tec, _, inc, _ = self._setup(db, "t2", "EN_CAMINO")
        url = f"/tecnicos/incidente/{inc.ID_INCIDENTE}/estado"
        resp = client.patch(url, json={"nuevo_estado": "EN_PROCESO"}, headers=_auth_headers(u_tec))
        assert resp.status_code == 200, resp.text
        assert resp.json()["estado"] == "EN_PROCESO"

    def test_en_proceso_a_atendido_libera_tecnico(self, client, db):
        u_tec, tec, inc, _ = self._setup(db, "t3", "EN_PROCESO")
        url = f"/tecnicos/incidente/{inc.ID_INCIDENTE}/estado"

        with patch("app.application.use_cases.payment_service.crear_pago_pendiente") as mock_pay:
            mock_pay.return_value = MagicMock(ID_PAGO=uuid.uuid4(), MONTO=100)
            resp = client.patch(
                url, json={"nuevo_estado": "ATENDIDO"}, headers=_auth_headers(u_tec)
            )

        assert resp.status_code == 200, resp.text
        assert resp.json()["estado"] == "ATENDIDO"

        # Técnico debe quedar disponible
        db.expire_all()
        tec_reloaded = db.get(TECNICOS, tec.ID_TECNICO)
        assert tec_reloaded.DISPONIBLE is True

    def test_transicion_invalida_salto_retorna_400(self, client, db):
        u_tec, _, inc, _ = self._setup(db, "t4", "ASIGNADO")
        url = f"/tecnicos/incidente/{inc.ID_INCIDENTE}/estado"
        # Salto inválido: ASIGNADO → ATENDIDO (se salta EN_CAMINO y EN_PROCESO)
        resp = client.patch(url, json={"nuevo_estado": "ATENDIDO"}, headers=_auth_headers(u_tec))
        assert resp.status_code == 400
        assert "Transición inválida" in resp.json()["detail"]

    def test_tecnico_no_asignado_retorna_403(self, client, db):
        u_t = _make_user(db, "taller_t5@t.com", "TALLER")
        taller = _make_taller(db, u_t)

        u_tec_asignado = _make_user(db, "tech_t5a@t.com", "TECNICO")
        tec_asignado = _make_tecnico(db, taller, u_tec_asignado)

        u_tec_otro = _make_user(db, "tech_t5b@t.com", "TECNICO")
        _make_tecnico(db, taller, u_tec_otro)

        u_cli = _make_user(db, "cli_t5@t.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, "ASIGNADO")
        _make_asignacion(db, inc, taller, tec_asignado)
        db.commit()

        url = f"/tecnicos/incidente/{inc.ID_INCIDENTE}/estado"
        resp = client.patch(
            url,
            json={"nuevo_estado": "EN_CAMINO"},
            headers=_auth_headers(u_tec_otro),
        )
        assert resp.status_code == 403
        assert "asignado" in resp.json()["detail"].lower()

    def test_historial_registrado_tras_cambio(self, client, db):
        u_tec, _, inc, _ = self._setup(db, "t6", "ASIGNADO")
        url = f"/tecnicos/incidente/{inc.ID_INCIDENTE}/estado"
        client.patch(url, json={"nuevo_estado": "EN_CAMINO"}, headers=_auth_headers(u_tec))

        registros = (
            db.query(HISTORIAL_INCIDENTES)
            .filter(HISTORIAL_INCIDENTES.ID_INCIDENTE == inc.ID_INCIDENTE)
            .all()
        )
        assert len(registros) >= 1
        estados = [r.ESTADO for r in registros]
        assert any(e == "EN_CAMINO" or (hasattr(e, "value") and e.value == "EN_CAMINO") for e in estados)


# ═════════════════════════════════════════════════════════════════════════════
# TEST 4 — POST /tecnicos/crear-con-usuario
# ═════════════════════════════════════════════════════════════════════════════

class TestCrearTecnicoConUsuario:

    def test_crea_usuario_y_tecnico_atomicamente(self, client, db):
        u_t = _make_user(db, "taller_cu1@test.com", "TALLER")
        _make_taller(db, u_t)
        db.commit()

        resp = client.post(
            "/tecnicos/crear-con-usuario",
            json={
                "nombre_completo": "Nuevo Técnico",
                "correo_electronico": "nuevo_tec1@test.com",
                "contrasena": "Segura123!",
                "telefono": "70000001",
            },
            headers=_auth_headers(u_t),
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["id_usuario"] is not None

        nuevo_usr = (
            db.query(USUARIOS)
            .filter(USUARIOS.CORREO_ELECTRONICO == "nuevo_tec1@test.com")
            .first()
        )
        assert nuevo_usr is not None
        rol = nuevo_usr.ROL
        rol_str = rol.value if hasattr(rol, "value") else str(rol)
        assert rol_str == "TECNICO"

    def test_tecnico_creado_puede_loguearse(self, client, db):
        u_t = _make_user(db, "taller_cu2@test.com", "TALLER")
        _make_taller(db, u_t)
        db.commit()

        client.post(
            "/tecnicos/crear-con-usuario",
            json={
                "nombre_completo": "Login Técnico",
                "correo_electronico": "login_tec@test.com",
                "contrasena": "Segura123!",
            },
            headers=_auth_headers(u_t),
        )

        resp = client.post("/auth/login", json={
            "correo_electronico": "login_tec@test.com",
            "contrasena": "Segura123!",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_email_duplicado_retorna_400(self, client, db):
        u_t = _make_user(db, "taller_cu3@test.com", "TALLER")
        _make_taller(db, u_t)
        _make_user(db, "existe@test.com", "TECNICO")
        db.commit()

        resp = client.post(
            "/tecnicos/crear-con-usuario",
            json={
                "nombre_completo": "Dup Técnico",
                "correo_electronico": "existe@test.com",
                "contrasena": "Segura123!",
            },
            headers=_auth_headers(u_t),
        )
        assert resp.status_code == 400
        assert "correo" in resp.json()["detail"].lower()

    def test_cliente_no_puede_crear_tecnico(self, client, db):
        u_cli = _make_user(db, "cli_nocrea@test.com", "CLIENTE")
        db.commit()

        resp = client.post(
            "/tecnicos/crear-con-usuario",
            json={
                "nombre_completo": "Intruso",
                "correo_electronico": "intruso@test.com",
                "contrasena": "Segura123!",
            },
            headers=_auth_headers(u_cli),
        )
        assert resp.status_code == 403
