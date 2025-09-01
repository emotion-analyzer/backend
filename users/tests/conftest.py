from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session, SQLModel

from users.database.session import create_db_and_tables, engine
from users.main import app


@pytest.fixture(autouse=True)
def client():
    """Provide a test client for the FastAPI app."""
    create_db_and_tables()
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def truncate_tables():
    """Clean all tables after each test."""
    yield  # Run the test first

    with Session(engine) as session:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
