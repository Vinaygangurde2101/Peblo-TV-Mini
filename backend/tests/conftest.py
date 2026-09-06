import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User, UserRole
from app.auth.password import hash_password

import os
from app.core.config import settings

# Use TEST_DATABASE_URL if set, or postgresql in CI, or dedicated test_runner.db locally.
# Ensures development database (peblo.db) is NEVER mutated by unit tests.
TEST_DB_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DB_URL:
    if settings.DATABASE_URL.startswith("postgresql"):
        TEST_DB_URL = settings.DATABASE_URL
    else:
        test_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test_runner.db")).replace("\\", "/")
        TEST_DB_URL = f"sqlite:///{test_db_path}"

SQLALCHEMY_DATABASE_URL = TEST_DB_URL

is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")
engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({"pool_pre_ping": True})

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db: Session):
    user = User(
        email="test_admin@peblo.tv",
        password_hash=hash_password("admin_pass"),
        role=UserRole.ADMIN,
        full_name="Test Admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def editor_user(db: Session):
    user = User(
        email="test_editor@peblo.tv",
        password_hash=hash_password("editor_pass"),
        role=UserRole.EDITOR,
        full_name="Test Editor"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
