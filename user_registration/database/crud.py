from sqlmodel import select

from user_registration.model import User
from user_registration.schemas import RegisterUser

from user_registration.main import SessionDep


def register_new_user(new_user: RegisterUser, session: SessionDep):
    if get_user_by_username(new_user.username, session) is not None:
        return None
    user = User(username = new_user.username, email = new_user.email, password = new_user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return get_user_by_username(new_user.username, session)

def get_user_by_username(username: str, session: SessionDep) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

