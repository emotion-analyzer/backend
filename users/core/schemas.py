from pydantic import BaseModel, EmailStr


class UserDetails(BaseModel):
    """User details to be returned on log in."""
    id: int
    username: str
    display_name: str
    avatar_url: str | None
    email: EmailStr


class NewUserDetails(BaseModel):
    """New user details for updating users."""
    username: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = None
    confirm_password: str | None = None


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


class PasswordReset(BaseModel):
    """Password reset details."""
    token: str
    new_password: str


class PasswordResetRequest(BaseModel):
    """Password reset request details."""
    email: EmailStr
