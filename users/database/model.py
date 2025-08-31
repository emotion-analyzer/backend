from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Represents a single user in the application."""

    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    display_name: str = Field(nullable=False)
    avatar_url: str = Field(nullable=True)
    email: EmailStr = Field(default=None, unique=True, nullable=False)
    password_hash: str = Field(default=None, nullable=False)
    active: bool = Field(default=True, nullable=False)
