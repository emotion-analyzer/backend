from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from user_registration.database.session import create_db_and_tables, SessionDep
from user_registration.database.crud import register_new_user

from user_registration.schemas import RegisterUser

from user_registration.exceptions.exceptions import UserAlreadyExistsError


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/api/users/register")
async def register(new_user: RegisterUser, session: SessionDep):
    try:
        registered_user = register_new_user(new_user, session)
        return {"message": "Usuario registrado exitosamente",
                "id": registered_user.id}
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail= e.message)
