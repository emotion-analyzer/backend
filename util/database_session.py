from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine


engine = None

def init_engine(database_url: str):
    global engine
    engine = create_engine(database_url)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
