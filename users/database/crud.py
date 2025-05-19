from sqlmodel import select

from users.core.hashing import get_hash
from users.core.schemas import RegisterUser
from users.database.model import User
from users.database.session import SessionDep
from users.exceptions.exceptions import (UserAlreadyExistsError,
                                         UserDoesntExistError)


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


def get_user_by_email(email: str, session: SessionDep) -> User | None:
    """Return user with given email or None if not found."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def verify_user_existence(email: str, session: SessionDep) -> bool:
    """Return True if the email belongs to a user, False otherwise."""
    return get_user_by_email(email, session) is not None


def delete_user_from_db(user_id: int, session: SessionDep):
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if user is None:
        raise UserDoesntExistError
    session.delete(user)
    session.commit()

# def set_password_hash_for_user(
#     user: RegisterUser, hashed_password: str, session: SessionDep
# ) -> None:
#     user.password_hash = hashed_password
#     session.commit()
