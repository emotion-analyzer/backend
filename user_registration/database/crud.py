from sqlmodel import select

from user_registration.core.schemas import LoginUser, RegisterUser
from user_registration.database.model import User
from user_registration.database.session import SessionDep
from user_registration.exceptions.exceptions import UserAlreadyExistsError


def register_new_user(user: RegisterUser, session: SessionDep):
    """Register a new user in the database and return it."""
    if get_user_by_username(user.username, session) is not None:
        raise UserAlreadyExistsError("nombre de usuario")
    if get_user_by_email(user.email, session) is not None:
        raise UserAlreadyExistsError("email")
    user = User(
        username=user.username, email=user.email, password=user.password
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


def verify_user_password(login_data: LoginUser, session: SessionDep) -> bool:
    """Return True if password/email match login_data, False otherwise."""
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()
    if user.password != login_data.password:
        return False
    return True
