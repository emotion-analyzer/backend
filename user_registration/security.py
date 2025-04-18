import jwt

from user_registration.config import config
from user_registration.database.crud import (
    verify_user_existence,
    verify_user_password,
)
from user_registration.database.session import SessionDep
from user_registration.exceptions.exceptions import AuthError
from user_registration.schemas import LoginUser


def get_token(login: LoginUser, session: SessionDep):
    """Return JWT token if given login data is valid."""
    if not verify_user_existence(login.email, session):
        raise AuthError("Usuario no encontrado.")
    if not verify_user_password(login, session):
        raise AuthError("Contraseña invalida.")
    encoded_jwt = jwt.encode(
        {"email": login.email}, config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt


def decode_token(token):
    """Decode JWT and return decoded data."""
    try:
        # Just a placeholder. Will move to a secure config file.
        return jwt.decode(token, config.SECRET_KEY, algorithms=config.ALGORITHM)
    except jwt.InvalidTokenError as e:
        raise AuthError("Token de seguridad invalido.") from e
