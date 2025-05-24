from pydantic import BaseModel, EmailStr


class RegisterUser(BaseModel):
    """New user's registration details."""

    username: str
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    """User's data required for a login."""

    email: EmailStr
    password: str


class NewUser(BaseModel):
    """User data returned after successful registration."""

    id: int


class PasswordReset(BaseModel):
    """Password reset details."""
    token: str
    new_password: str


class PasswordResetRequest(BaseModel):
    """Password reset request details."""
    email: EmailStr
