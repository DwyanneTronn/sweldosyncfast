import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session
from app.models import Tenant, Employee, PayrollRun, PayrollLineItem, PayrollResult # Import all to register metadata

# Use StaticPool to share the in-memory connection across threads/sessions
sqlite_file_name = ":memory:"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(
    sqlite_url, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="api_key")
def api_key_fixture(session: Session):
    tenant = Tenant(name="Test Corp", api_key="test-secret-key", is_active=True)
    session.add(tenant)
    session.commit()
    return tenant.api_key
