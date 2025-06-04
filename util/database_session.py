from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine


engine = None  # global placeholder

def init_engine(database_url: str):
    global engine
    engine = create_engine(database_url)

def get_session():
    if engine is None:
        raise RuntimeError("Engine not initialized. Call init_engine first.")
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def create_db_and_tables():
    if engine is None:
        raise RuntimeError("Engine not initialized. Call init_engine first.")
    SQLModel.metadata.create_all(engine)
