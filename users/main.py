from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from users.core.password_reset import send_password_reset_email
from users.core.schemas import (
    LoginUser,
    PasswordReset,
    PasswordResetRequest,
    RegisterUser,
)
from users.core.security import get_password_reset_token, get_token, verify_token
from users.database.crud import (
    delete_user_from_db,
    get_user_by_email,
    register_new_user,
    update_password,
)
from users.database.session import SessionDep, create_db_and_tables
from users.exceptions.exceptions import (
    AuthError,
    UserAlreadyExistsError,
    UserDoesntExistError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database and tables before the app runs."""
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/register")
async def register(new_user: RegisterUser, session: SessionDep):
    """Register a new user in the application.

    Returns:
        id: the resulting id for the new registered user.
    """
    try:
        user = register_new_user(new_user, session)
        return {"message": "Usuario registrado exitosamente", "id": user.id}
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail=e.message) from e


@app.post("/login")
async def login(login_data: LoginUser, session: SessionDep):
    """Return JWT for registered user.

    Returns:
        access_token: the resulting JWT for the user.
        token_type: always "bearer".
    """
    try:
        user = get_user_by_email(login_data.email, session)
        if user is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail="Usuario no encontrado.")
        jwt = get_token(login_data, user, session)
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    return {"access_token": jwt, "token_type": "bearer"}


@app.post("/reset-password")
async def password_reset(password_reset: PasswordReset,
                         session: SessionDep):
    """Update user password.

    Returns:
        None

    HTTP Status Codes:
        200 OK: If the password reset was successful.
        401 Unauthorized: If the token format is invalid in any way
        If the old password is incorrect.
        404 Not Found: If the token has a valid format but there is no such user.
    """
    try:
        update_password(password_reset, session)
    except UserDoesntExistError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=e.message) from e
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    return {"detail": "Contraseña actualizada exitosamente."}


@app.post("/forgot-password")
async def password_reset_mail(password_reset_request: PasswordResetRequest,
                              session: SessionDep):
    """Send mail to initiate password reset.

    Returns:
        None

    HTTP Status Codes:
        200 OK: After attempting to send a password reset email (even if it fails!).
    """
    user = get_user_by_email(password_reset_request.email, session)
    if user is not None:
        token = get_password_reset_token(user.email)
        await send_password_reset_email(password_reset_request.email, token)
    return {"message": "Si el correo está registrado, "
                       "se han enviado instrucciones para restablecer la contraseña."}


@app.delete("/{user_id}")
async def delete_user(user_id: int, session: SessionDep,
                      access_token: str = Depends(oauth2_scheme)):
    """Delete registered user with specified id.

    Returns:
        None

    Raises:
        AuthError: If the user_id doesn't match the token-encoded id.

    HTTP Status Codes:
        200 OK: If the user has been successfully deleted.
        401 Unauthorized: If the token is invalid in any way (format, wrong id, etc.)
    """
    try:
        verify_token(user_id, access_token)
        delete_user_from_db(user_id, session)
    except UserDoesntExistError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=e.message) from e
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    return {"detail": "Usuario borrado exitosamente."}
