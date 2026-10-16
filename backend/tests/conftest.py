import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# A dedicated test database is mandatory; never default to an application DB.
url = os.environ.get("TEST_DATABASE_URL", "sqlite://")
os.environ["DATABASE_URL"] = url
from app.db import Base, get_db
from app.main import app
from sqlalchemy.pool import StaticPool

@pytest.fixture
def client():
    kwargs = {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool} if url == "sqlite://" else {}
    engine = create_engine(url, **kwargs)
    if url == "sqlite://":
        Base.metadata.create_all(engine)
    else:
        # CI/local runner must apply Alembic first. Do not mask migration failures.
        with engine.begin() as conn:
            assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0001_create_tasks"
            conn.execute(text("TRUNCATE tasks RESTART IDENTITY"))
    factory = sessionmaker(bind=engine)
    def override():
        with factory() as session:
            yield session
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()
