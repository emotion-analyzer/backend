import jwt
from user_registration.config import config
from user_registration.core.hashing import verify_password
from user_registration.core.schemas import LoginUser
from user_registration.database.crud import (
    get_user_by_email,
    verify_user_existence,
)
from user_registration.database.session import SessionDep
from user_registration.exceptions.exceptions import AuthError


def get_token(login: LoginUser, session: SessionDep):
    """Return a JWT token if given login data is valid."""
    if not verify_user_existence(login.email, session):
        raise AuthError("Usuario no encontrado.")
    user = get_user_by_email(login.email, session)
    if not verify_password(login.password, user, session):
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
