from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from users.config import config
from users.core.image_storage import s3_storage_initialize
from users.core.password_reset import send_password_reset_email
from users.core.schemas import (
    LoginResponse,
    LoginUser,
    PasswordChange,
    PasswordReset,
    PasswordResetRequest,
    RegisterUser,
    UserDelete,
    UserDetails,
)
from users.core.security import (
    decode_token,
    get_password_reset_token,
    get_token,
)
from users.database.crud import (
    delete_user_from_db,
    get_user_by_email,
    register_new_user,
    update_password,
    update_user_avatar,
    update_user_password,
)
from users.database.session import SessionDep, create_db_and_tables
from users.exceptions.exceptions import (
    AuthError,
    ImageFormatError,
    UserAlreadyExistsError,
    UserDoesntExistError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database and tables before the app runs."""
    create_db_and_tables()
    if not config.TESTING:
        app.state.minio_client = s3_storage_initialize()
    else:
        app.state.minio_client = None
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


@app.post("/login", response_model=LoginResponse)
async def login(login_data: LoginUser, session: SessionDep):
    """Return JWT for registered user.

    Returns:
        access_token: the resulting JWT for the user.
        token_type: always "bearer".
    """
    try:
        user = get_user_by_email(login_data.email, session)
        jwt = get_token(login_data, user, session)
        user_details = UserDetails(id = user.id,
                                   username = user.username,
                                   avatar_url = user.avatar_url,
                                   email = user.email)
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    return LoginResponse(access_token=jwt, token_type="bearer", user=user_details)


@app.get("/me", response_model=UserDetails)
async def get_user_details_route(session: SessionDep,
                                 access_token: str = Depends(oauth2_scheme)):
    """Returns user details using JWT encoded data.

    Returns:
        id: str
        username: str
        display_name: str
        avatar_url: str | None
        email:

    HTTP Status Codes:
        200 OK: If the user details were successfully retrieved.
        401 Unauthorized: If the token is invalid in any way (format, expired, etc.)

    """
    try:
        decoded_token = decode_token(access_token)
        user = get_user_by_email(decoded_token["email"], session)
        user_details = UserDetails(id = user.id,
                                   username = user.username,
                                   avatar_url = user.avatar_url,
                                   email = user.email)
    except UserDoesntExistError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=e.message) from e
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    return user_details


@app.post("/me/change-password")
async def update_user_details_route(password_update: PasswordChange,
                                    session: SessionDep,
                                    access_token: str = Depends(oauth2_scheme)):
    """Updates user password.

    HTTP Status Codes:
        200 OK: If the user details were successfully retrieved.
        401 Unauthorized: If the token is invalid in any way (format, expired, etc.)

    """
    try:
        decoded_token = decode_token(access_token)
        update_user_password(password_update, decoded_token["id"],
                             app.state.minio_client, session)
    except UserDoesntExistError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=e.message) from e
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    return {"message": "La contraseña ha sido actualizada correctamente."}


@app.put("/me/avatar")
async def upload_avatar(session: SessionDep,
                        avatar: UploadFile = File(...),
                        access_token: str = Depends(oauth2_scheme)):
    """Updates user avatar.

    HTTP Status Codes:
        200 OK: If the user avatar was successfully updated.
        401 Unauthorized: If the token is invalid in any way (format, expired, etc.)

    """
    try:
        file = await avatar.read()
        extension = avatar.content_type.split("/")[-1]
        decoded_token = decode_token(access_token)
        avatar_url = update_user_avatar(file, extension, decoded_token["id"],
                                        app.state.minio_client, session)
    except UserDoesntExistError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=e.message) from e
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    except ImageFormatError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=e.message) from e
    return {"avatar_url": avatar_url,
            "message": "Avatar actualizado correctamente."}

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
    return {"message": "La contraseña ha sido restablecida correctamente."}


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


@app.delete("/me")
async def delete_user(
        delete_details: UserDelete,
        session: SessionDep,
        access_token: str = Depends(oauth2_scheme)):
    """Delete user referenced by JWT encoded data.

    Returns:
        None

    Raises:
        AuthError: If the user_id doesn't match the token-encoded id.

    HTTP Status Codes:
        200 OK: If the user has been successfully deleted.
        401 Unauthorized: If the token is invalid in any way (format, wrong id, etc.)
    """
    try:
        decoded_token = decode_token(access_token)
        delete_user_from_db(delete_details, decoded_token["id"], session)
    except UserDoesntExistError as e:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=e.message) from e
    except AuthError as e:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=e.message) from e
    return {"message": "La cuenta ha sido eliminada correctamente."}
