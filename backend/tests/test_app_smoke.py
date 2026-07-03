from fastapi.testclient import TestClient


def test_health_ok():
    from app.main import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert "environment" in body


def test_settings_loads_from_env():
    from app.core.config import settings

    assert settings.APP_NAME.startswith("Plataforma")
    assert settings.SECRET_KEY
    assert settings.POSTGRES_USER


def test_models_metadata_has_tables():
    import app.models  # noqa: F401
    from app.core.database import Base

    names = {t.name for t in Base.metadata.sorted_tables}
    assert "usuarios" in names
    assert "incidentes" in names
