from pydantic import BaseModel


class RegisterUser(BaseModel):
    """New user's registration details."""

    username: str
    email: str
    password: str


class LoginUser(BaseModel):
    """User's data required for a login."""

    email: str
    password: str


class NewUser(BaseModel):
    """User data returned after successful registration."""

    id: int

class PasswordReset(BaseModel):
    old_password: str
    new_password: str
