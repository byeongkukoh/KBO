from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import clear_settings_cache
from app.db.base import Base
from app.db.session import clear_db_caches, get_engine
from app.main import create_app
from app.models import game, stats, sync, team  # noqa: F401


@pytest.fixture
def sqlite_db_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    db_path = tmp_path / "test.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    clear_settings_cache()
    clear_db_caches()
    engine = get_engine()
    Base.metadata.create_all(engine)
    yield db_url
    Base.metadata.drop_all(engine)
    clear_db_caches()
    clear_settings_cache()


@pytest.fixture
def client(sqlite_db_url: str) -> TestClient:
    app = create_app()
    return TestClient(app)
