import time
from typing import Any

import jwt
from pydantic import EmailStr

from users.config import config
from users.core.hashing import verify_password
from users.core.schemas import LoginUser
from users.database.model import User
from users.database.session import SessionDep
from users.exceptions.exceptions import AuthError


def get_token(login: LoginUser, user: User,
              session: SessionDep):
    """Return a JWT token if given login data is valid."""
    if not verify_password(login.password, user, session):
        raise AuthError("Contraseña invalida.")
    expiration_time = int(time.time()) + config.EXPIRATION_MINUTES_LOGIN * 60
    encoded_jwt = encode_token(
        {"id": user.id, "email": login.email, "iss": "users",
         "exp": expiration_time})
    return encoded_jwt

def get_password_reset_token(email: EmailStr) -> str:
    """Return a JWT token for given email."""
    expiration_time = int(time.time()) + config.EXPIRATION_MINUTES_PW_RESET * 60
    return encode_token({"email": email, "iss": "users", "exp": expiration_time})

def encode_token(data: dict[str, Any]) -> str:
    """Return token with encoded data."""
    return jwt.encode( data, config.SECRET_KEY, algorithm=config.ALGORITHM,
        headers={"alg": config.ALGORITHM, "typ": "JWT", "kid": config.KONG_KEY})

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
