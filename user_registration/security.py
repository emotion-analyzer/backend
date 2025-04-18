from user_registration.database.session import SessionDep
from user_registration.schemas import LoginUser

from user_registration.exceptions.exceptions import AuthError

from user_registration.database.crud import verify_user_existence

from user_registration.database.crud import verify_user_password

import jwt


def get_token(login_data: LoginUser, session: SessionDep):
    if not verify_user_existence(login_data.email, session):
        raise AuthError("Usuario no encontrado.")
    if not verify_user_password(login_data, session):
        raise AuthError("Contraseña invalida.")
    # Just a placeholder. Will move to a secure config file.
    encoded_jwt = jwt.encode({"email": login_data.email}, "secret", algorithm="HS256")
    return encoded_jwt


def decode_token(token):
    try:
        # Just a placeholder. Will move to a secure config file.
        return jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise AuthError("Token de seguridad invalido.")
