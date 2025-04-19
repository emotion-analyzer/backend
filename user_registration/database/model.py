from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Represents a single user in the application."""

    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(default=None, unique=True, nullable=False)
    password: str = Field(default=None)
