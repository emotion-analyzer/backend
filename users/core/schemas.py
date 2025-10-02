from pydantic import BaseModel, EmailStr


class UserDetails(BaseModel):
    """User details to be returned on log in."""
    id: int
    username: str
    avatar_url: str | None
    email: EmailStr


class PasswordChange(BaseModel):
    """Data required for a password change."""
    current_password: str
    new_password: str


class LoginResponse(BaseModel):
    """User login response."""
    access_token: str
    token_type: str
    user: UserDetails

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

class UserDelete(BaseModel):
    """Data required to delete a user."""
    current_password: str
    reason: str | None = None

class PasswordReset(BaseModel):
    """Password reset details."""
    token: str
    new_password: str


class PasswordResetRequest(BaseModel):
    """Password reset request details."""
    email: EmailStr
