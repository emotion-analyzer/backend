from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from user_registration.database.session import create_db_and_tables, SessionDep
from user_registration.database.crud import register_new_user

from user_registration.security import get_token

from user_registration.schemas import RegisterUser, LoginUser

from user_registration.exceptions.exceptions import UserAlreadyExistsError, AuthError


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/api/users/register")
async def register(new_user: RegisterUser, session: SessionDep):
    try:
        registered_user = register_new_user(new_user, session)
        return {"message": "Usuario registrado exitosamente", "id": registered_user.id}
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)


@app.post("/api/users/login")
async def login(login_data: LoginUser, session: SessionDep):
    try:
        jwt = get_token(login_data, session)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=e.message)
    return {"access_token": jwt, "token_type": "bearer"}
