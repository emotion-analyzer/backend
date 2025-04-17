from fastapi import FastAPI

from backend.user_registration.schemas import RegisterUser

app = FastAPI()


@app.post("/api/users/register")
async def register(new_user: RegisterUser):
    return {"message": "Usuario registrado exitosamente"}
