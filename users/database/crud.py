from pydantic import EmailStr
from sqlmodel import select

from users.core.hashing import get_hash, verify_password
from users.core.schemas import PasswordReset, RegisterUser
from users.core.security import decode_token
from users.database.model import User
from users.database.session import SessionDep
from users.exceptions.exceptions import (
    AuthError,
    UserAlreadyExistsError,
    UserDoesntExistError,
)


def register_new_user(user: RegisterUser, session: SessionDep) -> User | None:
    """Register a new user in the database and return it."""
    if get_user_by_username(user.username, session) is not None:
        raise UserAlreadyExistsError("nombre de usuario")
    if get_user_by_email(user.email, session) is not None:
        raise UserAlreadyExistsError("email")
    user = User(
        username=user.username,
        email=user.email,
        password_hash=get_hash(user.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return get_user_by_username(user.username, session)


def get_user_by_username(username: str, session: SessionDep) -> User | None:
    """Return user with given username or None if not found."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def get_user_by_email(email: EmailStr, session: SessionDep) -> User | None:
    """Return user with given email or None if not found."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def delete_user_from_db(user_id: int, session: SessionDep):
    """Delete user from database, raise exception if not found."""
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if user is None:
        raise UserDoesntExistError
    session.delete(user)
    session.commit()

def update_password(password_reset: PasswordReset,
                    access_token: str, session: SessionDep) -> None:
    """Update hashed password in the database."""
    payload = decode_token(access_token)
    statement = select(User).where(User.id == payload["id"])
    user = session.exec(statement).first()
    if user is None:
        raise UserDoesntExistError
    if not verify_password(password_reset.old_password, user, session):
        raise AuthError("Contraseña vieja invalida.")
    user.password_hash = get_hash(password_reset.new_password)
    session.add(user)
    session.commit()

