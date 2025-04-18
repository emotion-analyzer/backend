from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from user_registration.database.session import create_db_and_tables, SessionDep
from user_registration.database.crud import register_new_user

from user_registration.schemas import RegisterUser


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/api/users/register")
async def register(new_user: RegisterUser, session: SessionDep):
    registered_user = register_new_user(new_user, session)
    if registered_user is None:
        raise HTTPException(status_code=409, detail= "Usuario ya registrado" )
    return {"message": "Usuario registrado exitosamente",
            "id": registered_user.id}
