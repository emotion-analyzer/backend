import jwt

from users.config import config
from users.core.hashing import verify_password
from users.core.schemas import LoginUser
from users.database.crud import (
    get_user_by_email,
    verify_user_existence,
)
from users.database.session import SessionDep
from users.exceptions.exceptions import AuthError


def get_token(login: LoginUser, session: SessionDep):
    """Return a JWT token if given login data is valid."""
    if not verify_user_existence(login.email, session):
        raise AuthError("Usuario no encontrado.")
    user = get_user_by_email(login.email, session)
    if not verify_password(login.password, user, session):
        raise AuthError("Contraseña invalida.")
    encoded_jwt = jwt.encode(
        {"email": login.email}, config.SECRET_KEY, algorithm=config.ALGORITHM),
    headers = {"alg": config.ALGORITHM, "typ": "JWT","kid": config.KONG_KEY}

    return encoded_jwt


def decode_token(token):
    """Decode JWT and return decoded data."""
    try:
        # Just a placeholder. Will move to a secure config file.
        return jwt.decode(token, config.SECRET_KEY, algorithms=config.ALGORITHM)
    except jwt.InvalidTokenError as e:
        raise AuthError("Token de seguridad invalido.") from e
