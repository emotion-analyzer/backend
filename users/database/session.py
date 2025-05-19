from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from users.config import config

engine = create_engine(config.DATABASE_URL)


def get_session():
    """Initiate SQLModel session then yield it."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    """Create the database and its tables."""
    SQLModel.metadata.create_all(engine)
