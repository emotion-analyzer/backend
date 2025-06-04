import time
from typing import Any

import jwt
from pydantic import EmailStr

from users.config import config
from users.core.hashing import verify_password
from users.core.schemas import LoginUser
from users.database.model import User
from util.database_session import SessionDep
from users.exceptions.exceptions import AuthError


def get_token(login: LoginUser, user: User,
              session: SessionDep):
    """Return a JWT token if given login data is valid."""
    if not verify_password(login.password, user, session):
        raise AuthError("Contraseña invalida.")
    encoded_jwt = encode_token(
        {"id": user.id, "email": login.email},
        expiration_time=config.JWT.EXPIRATION_MINUTES_LOGIN * 60)
    return encoded_jwt

def get_password_reset_token(email: EmailStr) -> str:
    """Return a JWT token for given email."""
    return encode_token({"email": email},
                        expiration_time=config.JWT.EXPIRATION_MINUTES_PW_RESET * 60)

def encode_token(data: dict[str, Any], expiration_time: int) -> str:
    """Return token with encoded data."""
    data.update({
        "iss": "users",
        "exp": int(time.time()) + expiration_time
    })
    return jwt.encode(data, config.JWT.KEY, algorithm=config.JWT.ALGORITHM,
        headers={"alg": config.JWT.ALGORITHM, "typ": "JWT", "kid": config.KONG.KEY})

def decode_token(token):
    """Decode JWT and return decoded data."""
    try:
        return jwt.decode(token, config.JWT.KEY, algorithms=config.JWT.ALGORITHM)
    except jwt.InvalidTokenError as e:
        raise AuthError("Token de seguridad invalido.") from e


def verify_token(user_id: int, token):
    """Verify encoded data in token."""
    try:
        payload = jwt.decode(token, config.JWT.KEY, algorithms=config.JWT.ALGORITHM)
    except jwt.InvalidTokenError as e:
        raise AuthError("Token de seguridad invalido.") from e
    if payload["id"] != user_id:
        raise AuthError("ID de usuario no coincide.")
