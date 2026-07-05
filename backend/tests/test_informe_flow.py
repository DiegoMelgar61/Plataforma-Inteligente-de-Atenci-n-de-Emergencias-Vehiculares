"""
Smoke tests del informe de servicio en PDF generado con IA al finalizar un
incidente (transición a ATENDIDO).

Cubre:
- Generación + persistencia con IA disponible (fila + PDF en disco).
- Tolerancia a fallos: si la IA falla, el PDF se genera igual con textos de
  respaldo y GENERADO_POR_IA=False (nunca rompe la transición).
- Endpoint de consulta con aislamiento por tenant/propiedad.

Estrategia: TestClient + SQLite en memoria, Geography parcheada a Text,
UPLOADS_DIR redirigido a un tmp, y run_gemini mockeado.
"""
from pathlib import Path
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

from app.core.config import settings  # noqa: E402
from app.core.database import Base, get_db  # noqa: E402
from app.core.security import crear_access_token, hashear_contrasena  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.assignments.models import ASIGNACIONES  # noqa: E402
from app.modules.incidents.models import INCIDENTES  # noqa: E402
from app.modules.informes import service as informes_service  # noqa: E402
from app.modules.informes.models import INFORMES_SERVICIO  # noqa: E402
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
    # Re-afirma el override: otros módulos de test pisan el mismo singleton `app`.
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def uploads_tmp(tmp_path, monkeypatch):
    """Redirige el almacenamiento de PDFs a un directorio temporal."""
    monkeypatch.setattr(settings, "UPLOADS_DIR", tmp_path)
    yield


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

_CONTENIDO_IA_OK = {
    "resumen_incidente": "El cliente reportó una falla y fue atendido.",
    "diagnostico": "Batería descargada por luces encendidas.",
    "trabajo_realizado": "Se realizó arranque asistido y carga.",
    "estado_final": "Vehículo operativo, motor en marcha.",
    "recomendaciones_preventivas": "Revisar alternador y evitar dejar luces.",
    "proximos_pasos": "Visita al taller para chequeo del sistema de carga.",
}


def _make_user(db, correo: str, rol: str, nombre: str = "Test User") -> USUARIOS:
    u = USUARIOS(
        CORREO_ELECTRONICO=correo,
        HASH_CONTRASENA=hashear_contrasena("Segura123!"),
        NOMBRE_COMPLETO=nombre,
        ROL=rol,
        ACTIVO=True,
        ID_TENANT=1,
    )
    db.add(u)
    db.flush()
    return u


def _make_incidente(db, cliente: USUARIOS, estado: str = "ATENDIDO") -> INCIDENTES:
    inc = INCIDENTES(
        ID_USUARIO_CLIENTE=cliente.ID_USUARIO,
        UBICACION="POINT(-68.15 -16.50)",
        ESTADO=estado,
        PRIORIDAD="MEDIA",
        CLASIFICACION="BATERIA",
        ID_TENANT=1,
    )
    db.add(inc)
    db.flush()
    return inc


def _make_asignacion(db, incidente, cliente) -> ASIGNACIONES:
    u_taller = _make_user(db, f"taller_{incidente.ID_INCIDENTE}@t.com", "TALLER")
    taller = TALLERES(ID_USUARIO=u_taller.ID_USUARIO, NOMBRE_NEGOCIO="Taller Sur",
                      NIT=f"NIT-{u_taller.ID_USUARIO}", ID_TENANT=1)
    db.add(taller)
    db.flush()
    u_tec = _make_user(db, f"tec_{incidente.ID_INCIDENTE}@t.com", "TECNICO")
    tecnico = TECNICOS(ID_TALLER=taller.ID_TALLER, ID_USUARIO=u_tec.ID_USUARIO,
                       NOMBRE_COMPLETO="Tec Uno", DISPONIBLE=True)
    db.add(tecnico)
    db.flush()
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
# TEST 1 — Generación + persistencia con IA disponible
# ═════════════════════════════════════════════════════════════════════════════

class TestGeneracionInforme:

    def test_genera_y_persiste_con_ia(self, db):
        u_cli = _make_user(db, "cli_inf1@test.com", "CLIENTE", "Ana Cliente")
        inc = _make_incidente(db, u_cli)
        _make_asignacion(db, inc, u_cli)
        db.commit()

        with patch(
            "app.infrastructure.external_services.ai_service.run_gemini",
            return_value=dict(_CONTENIDO_IA_OK),
        ):
            informe = informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)

        assert informe is not None
        assert informe.GENERADO_POR_IA is True
        assert informe.URL_ARCHIVO.startswith(settings.INFORMES_URL_PREFIX)

        ruta = Path(settings.UPLOADS_DIR) / informe.CLAVE_ARCHIVO
        assert ruta.is_file()
        assert ruta.read_bytes().startswith(b"%PDF")

    def test_fallback_si_ia_falla_no_rompe(self, db):
        u_cli = _make_user(db, "cli_inf2@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli)
        _make_asignacion(db, inc, u_cli)
        db.commit()

        with patch(
            "app.infrastructure.external_services.ai_service.run_gemini",
            side_effect=RuntimeError("Gemini caído"),
        ):
            informe = informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)

        assert informe is not None
        assert informe.GENERADO_POR_IA is False
        ruta = Path(settings.UPLOADS_DIR) / informe.CLAVE_ARCHIVO
        assert ruta.is_file()
        assert ruta.read_bytes().startswith(b"%PDF")

    def test_regenerar_no_duplica_fila(self, db):
        u_cli = _make_user(db, "cli_inf3@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli)
        _make_asignacion(db, inc, u_cli)
        db.commit()

        with patch(
            "app.infrastructure.external_services.ai_service.run_gemini",
            return_value=dict(_CONTENIDO_IA_OK),
        ):
            informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)
            informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)

        total = (
            db.query(INFORMES_SERVICIO)
            .filter(INFORMES_SERVICIO.ID_INCIDENTE == inc.ID_INCIDENTE)
            .count()
        )
        assert total == 1


# ═════════════════════════════════════════════════════════════════════════════
# TEST 2 — Endpoint de consulta + aislamiento por propiedad/tenant
# ═════════════════════════════════════════════════════════════════════════════

class TestConsultaInforme:

    def test_cliente_dueno_obtiene_su_informe(self, client, db):
        u_cli = _make_user(db, "cli_inf4@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli)
        _make_asignacion(db, inc, u_cli)
        db.commit()

        with patch(
            "app.infrastructure.external_services.ai_service.run_gemini",
            return_value=dict(_CONTENIDO_IA_OK),
        ):
            informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)

        resp = client.get(
            f"/informes/incidents/{inc.ID_INCIDENTE}",
            headers=_auth_headers(u_cli),
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["id_incidente"] == inc.ID_INCIDENTE
        assert data["generado_por_ia"] is True
        assert data["url_archivo"].startswith(settings.INFORMES_URL_PREFIX)

    def test_otro_cliente_no_accede(self, client, db):
        u_cli = _make_user(db, "cli_inf5@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli)
        _make_asignacion(db, inc, u_cli)
        db.commit()
        with patch(
            "app.infrastructure.external_services.ai_service.run_gemini",
            return_value=dict(_CONTENIDO_IA_OK),
        ):
            informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)

        intruso = _make_user(db, "cli_intruso@test.com", "CLIENTE")
        db.commit()

        resp = client.get(
            f"/informes/incidents/{inc.ID_INCIDENTE}",
            headers=_auth_headers(intruso),
        )
        assert resp.status_code == 403, resp.text

    def test_404_si_no_hay_informe(self, client, db):
        u_cli = _make_user(db, "cli_inf6@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="EN_PROCESO")
        db.commit()

        resp = client.get(
            f"/informes/incidents/{inc.ID_INCIDENTE}",
            headers=_auth_headers(u_cli),
        )
        assert resp.status_code == 404, resp.text


# ═════════════════════════════════════════════════════════════════════════════
# TEST 3 — Envío del informe ya generado por correo (Resend), sin regenerarlo
# ═════════════════════════════════════════════════════════════════════════════

class TestEnvioCorreoInforme:

    def test_envia_correo_reutilizando_pdf_ya_persistido(self, db, monkeypatch):
        monkeypatch.setattr(settings, "RESEND_API_KEY", "re_test_key")
        monkeypatch.setattr(settings, "RESEND_FROM_EMAIL", "no-reply@test.com")

        u_cli = _make_user(db, "cli_correo1@test.com", "CLIENTE", "Beto Cliente")
        inc = _make_incidente(db, u_cli)
        _make_asignacion(db, inc, u_cli)
        db.commit()

        with patch(
            "app.infrastructure.external_services.ai_service.run_gemini",
            return_value=dict(_CONTENIDO_IA_OK),
        ):
            informe = informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)
        assert informe is not None

        with patch("app.modules.informes.service.httpx.post") as mock_post:
            mock_post.return_value.raise_for_status.return_value = None
            enviado = informes_service.enviar_correo_informe(db, inc.ID_INCIDENTE)

        assert enviado is True
        assert mock_post.call_count == 1
        _, kwargs = mock_post.call_args
        assert kwargs["json"]["to"] == ["cli_correo1@test.com"]
        assert kwargs["json"]["from"] == "no-reply@test.com"
        assert kwargs["json"]["attachments"][0]["filename"].endswith(".pdf")
        # El adjunto debe ser el PDF ya persistido, no uno regenerado en el momento.
        assert kwargs["json"]["attachments"][0]["content"]

    def test_sin_config_resend_no_envia(self, db, monkeypatch):
        monkeypatch.setattr(settings, "RESEND_API_KEY", None)
        monkeypatch.setattr(settings, "RESEND_FROM_EMAIL", None)

        u_cli = _make_user(db, "cli_correo2@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli)
        _make_asignacion(db, inc, u_cli)
        db.commit()

        with patch(
            "app.infrastructure.external_services.ai_service.run_gemini",
            return_value=dict(_CONTENIDO_IA_OK),
        ):
            informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)

        with patch("app.modules.informes.service.httpx.post") as mock_post:
            enviado = informes_service.enviar_correo_informe(db, inc.ID_INCIDENTE)

        assert enviado is False
        mock_post.assert_not_called()

    def test_fallo_resend_no_propaga_excepcion(self, db, monkeypatch):
        monkeypatch.setattr(settings, "RESEND_API_KEY", "re_test_key")
        monkeypatch.setattr(settings, "RESEND_FROM_EMAIL", "no-reply@test.com")

        u_cli = _make_user(db, "cli_correo3@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli)
        _make_asignacion(db, inc, u_cli)
        db.commit()

        with patch(
            "app.infrastructure.external_services.ai_service.run_gemini",
            return_value=dict(_CONTENIDO_IA_OK),
        ):
            informes_service.generar_y_persistir_informe(db, inc.ID_INCIDENTE)

        with patch(
            "app.modules.informes.service.httpx.post",
            side_effect=RuntimeError("Resend caído"),
        ):
            enviado = informes_service.enviar_correo_informe(db, inc.ID_INCIDENTE)

        assert enviado is False

    def test_sin_informe_persistido_no_envia(self, db, monkeypatch):
        monkeypatch.setattr(settings, "RESEND_API_KEY", "re_test_key")
        monkeypatch.setattr(settings, "RESEND_FROM_EMAIL", "no-reply@test.com")

        u_cli = _make_user(db, "cli_correo4@test.com", "CLIENTE")
        inc = _make_incidente(db, u_cli, estado="EN_PROCESO")
        db.commit()

        with patch("app.modules.informes.service.httpx.post") as mock_post:
            enviado = informes_service.enviar_correo_informe(db, inc.ID_INCIDENTE)

        assert enviado is False
        mock_post.assert_not_called()
