from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from users.config import config

connection_args = {"check_same_thread": False}
engine = create_engine(config.DATABASE_URL, connect_args=connection_args)


def get_session():
    """Initiate SQLModel session then yield it."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    """Create the database and its tables."""
    SQLModel.metadata.create_all(engine)
