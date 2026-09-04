import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User, UserRole
from app.auth.password import hash_password

# In-memory SQLite database for fast isolated unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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
