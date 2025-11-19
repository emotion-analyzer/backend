from pydantic import EmailStr
import sqlalchemy
from sqlmodel import select

from users.core.hashing import get_hash, verify_password
from users.core.image_storage import s3_store
from users.core.schemas import PasswordChange, PasswordReset, RegisterUser, UserDelete
from users.core.security import decode_token
from users.database.model import User
from users.database.session import SessionDep
from users.exceptions.exceptions import (
    AuthError,
    ImageFormatError,
    UserAlreadyExistsError,
    UserDoesntExistError,
)


def register_new_user(user: RegisterUser, session: SessionDep, app) -> User | None:
    """Register a new user in the database and return it."""
    if get_user_by_username(user.username, session, app) is not None:
        raise UserAlreadyExistsError("nombre de usuario")
    if get_user_by_email(user.email, session, app) is not None:
        raise UserAlreadyExistsError("email")
    user = User(
        username=user.username,
        display_name=user.username,
        email=user.email,
        password_hash=get_hash(user.password),
        active=True
    )
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except sqlalchemy.exc.OperationalError:
        app.state.logger.info("Failed database connection.")
        raise
    return get_user_by_username(user.username, session, app)


def get_user_by_username(username: str, session: SessionDep, app) -> User | None:
    """Return user with given username or None if not found."""
    statement = select(User).where(User.username == username,  User.active)
    try:
        user = session.exec(statement).first()
    except sqlalchemy.exc.OperationalError:
        app.state.logger.info("Failed database connection.")
        raise
    return user


def get_user_by_email(email: EmailStr, session: SessionDep, app) -> User | None:
    """Return user with given email or None if not found."""
    statement = select(User).where(User.email == email,  User.active)
    try:
        user = session.exec(statement).first()
    except sqlalchemy.exc.OperationalError:
        app.state.logger.info("Failed database connection.")
        raise
    return user


def get_user_by_id(user_id: int, session: SessionDep, app) -> User | None:
    """Return user with given email or None if not found."""
    statement = select(User).where(User.id == user_id,  User.active)
    try:
        user = session.exec(statement).first()
    except sqlalchemy.exc.OperationalError:
        app.state.logger.info("Failed database connection.")
        raise
    return user


def update_user_password(password_update: PasswordChange,
                         user_id: int, client,
                         session: SessionDep,
                         app) -> User | None:
    """Update user's details."""
    user = get_user_by_id(user_id, session, app)
    if user is None:
        raise UserDoesntExistError
    try:
        if not verify_password(password_update.current_password, user, session):
            raise AuthError("Contraseña inválida.")
        user.password_hash = get_hash(password_update.new_password)
        session.commit()
        session.refresh(user)
    except sqlalchemy.exc.OperationalError:
        app.state.logger.info("Failed database connection.")
        raise

def update_user_avatar(file, extension,
                       user_id: int, client,
                       session: SessionDep,
                       app) -> str:
    """Update user's details."""
    user = get_user_by_id(user_id, session, app)
    if user is None:
        raise UserDoesntExistError
    if extension not in ("jpeg", "jpg", "png"):
        raise ImageFormatError("Only JPEG/JPG and PNG allowed")
    avatar_url = s3_store(user_id, file, extension, client)
    user.avatar_url = avatar_url
    try:
        session.commit()
        session.refresh(user)
    except sqlalchemy.exc.OperationalError:
        app.state.logger.info("Failed database connection.")
        raise
    return avatar_url

def delete_user_from_db(user_delete: UserDelete, user_id: int, session: SessionDep, app):
    """Delete user from database, raise exception if not found."""
    user = get_user_by_id(user_id, session, app)
    if user is None:
        raise UserDoesntExistError
    if not verify_password(user_delete.current_password, user, session):
        raise AuthError("Contraseña inválida.")
    user.active = False
    try:
        session.commit()
        session.refresh(user)
    except sqlalchemy.exc.OperationalError:
        app.state.logger.info("Failed database connection.")
        raise

def update_password(password_reset: PasswordReset,
                    session: SessionDep, app) -> None:
    """Update hashed password in the database for user email specified in the token."""
    payload = decode_token(password_reset.token)
    user = get_user_by_email(payload["email"], session, app)
    if user is None:
        raise UserDoesntExistError
    user.password_hash = get_hash(password_reset.new_password)
    try:
        session.add(user)
        session.commit()
    except sqlalchemy.exc.OperationalError:
        app.state.logger.info("Failed database connection.")
        raise
