import time

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
    expiration_time = int(time.time()) + config.EXPIRATION_MINUTES * 60
    encoded_jwt = jwt.encode(
        {"id": user.id, "email": login.email, "iss": "users",
         "exp": expiration_time},
        config.SECRET_KEY, algorithm=config.ALGORITHM,
        headers={"alg": config.ALGORITHM, "typ": "JWT", "kid": config.KONG_KEY})
    return encoded_jwt


def decode_token(token):
    """Decode JWT and return decoded data."""
    try:
        return jwt.decode(token, config.SECRET_KEY, algorithms=config.ALGORITHM)
    except jwt.InvalidTokenError as e:
        raise AuthError("Token de seguridad invalido.") from e


def verify_token(user_id: int, token):
    """Verify encoded data in token."""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=config.ALGORITHM)
    except jwt.InvalidTokenError as e:
        raise AuthError("Token de seguridad invalido.") from e
    if payload["id"] != user_id:
        raise AuthError("ID de usuario no coincide.")
