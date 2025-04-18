from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from user_registration.database.crud import register_new_user
from user_registration.database.session import SessionDep, create_db_and_tables
from user_registration.exceptions.exceptions import (
    AuthError,
    UserAlreadyExistsError,
)
from user_registration.schemas import LoginUser, RegisterUser
from user_registration.security import get_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database and tables before the app runs."""
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/api/users/register")
async def register(new_user: RegisterUser, session: SessionDep):
    """Register a new user in the application.

    Returns:
        id: the resulting id for the new registered user.

    Raises:
        UserAlreadyExistsError If the email/username already exists.
    """
    try:
        user = register_new_user(new_user, session)
        return {"message": "Usuario registrado exitosamente", "id": user.id}
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message) from e


@app.post("/api/users/login")
async def login(login_data: LoginUser, session: SessionDep):
    """Return JWT for registered user.

    Returns:
        access_token: the resulting JWT for the user.
        token_type: always "bearer".

    Raises:
        AuthError: If the email doesn't exist or if the password is incorrect,
    """
    try:
        jwt = get_token(login_data, session)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=e.message) from e
    return {"access_token": jwt, "token_type": "bearer"}
