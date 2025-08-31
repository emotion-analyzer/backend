from pydantic import EmailStr
from sqlmodel import select

from users.core.hashing import get_hash, verify_password
from users.core.schemas import NewUserDetails, PasswordReset, RegisterUser
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
        display_name=user.username,
        email=user.email,
        password_hash=get_hash(user.password),
        active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return get_user_by_username(user.username, session)


def get_user_by_username(username: str, session: SessionDep) -> User | None:
    """Return user with given username or None if not found."""
    statement = select(User).where(User.username == username,  User.active)
    user = session.exec(statement).first()
    return user


def get_user_by_email(email: EmailStr, session: SessionDep) -> User | None:
    """Return user with given email or None if not found."""
    statement = select(User).where(User.email == email,  User.active)
    user = session.exec(statement).first()
    return user


def get_user_by_id(user_id: int, session: SessionDep) -> User | None:
    """Return user with given email or None if not found."""
    statement = select(User).where(User.id == user_id,  User.active)
    user = session.exec(statement).first()
    return user


def update_user_details(user_id: int,
                        details_update: NewUserDetails,
                        session: SessionDep) -> User | None:
    """Update user's details."""
    user = get_user_by_id(user_id, session)
    if user is None:
        raise UserDoesntExistError
    if details_update.email or details_update.new_password is not None:
        if not verify_password(details_update.current_password, user, session):
            raise AuthError("Contraseña inválida.")
    if details_update.new_password is not None:
        if details_update.new_password != details_update.confirm_password:
            raise AuthError("Contraseña de confirmación difiere de la nueva.")
    update_data = details_update.model_dump(exclude_unset=True, exclude_none=True)
    update_data.pop('confirm_password', None)
    update_data.pop('current_password', None)
    if 'new_password' in update_data:
        update_data['password_hash'] = get_hash(update_data.pop('new_password'))
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    session.commit()
    session.refresh(user)
    return user


def delete_user_from_db(user_id: int, session: SessionDep):
    """Delete user from database, raise exception if not found."""
    user = get_user_by_id(user_id, session)
    if user is None:
        raise UserDoesntExistError
    user.active = False
    session.commit()
    session.refresh(user)

def update_password(password_reset: PasswordReset,
                    session: SessionDep) -> None:
    """Update hashed password in the database for user email specified in the token."""
    payload = decode_token(password_reset.token)
    user = get_user_by_email(payload["email"], session)
    if user is None:
        raise UserDoesntExistError
    user.password_hash = get_hash(password_reset.new_password)
    session.add(user)
    session.commit()

