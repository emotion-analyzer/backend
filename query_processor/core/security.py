import jwt

from query_processor.config import config
from query_processor.exceptions.exceptions import AuthError


def decode_token(token):
    """Decode JWT and return decoded data."""
    try:
        jwt.decode(token, config.JWT.KEY, algorithms=config.JWT.ALGORITHM)
    except jwt.InvalidTokenError as e:
        raise AuthError("Token de seguridad invalido.") from e
