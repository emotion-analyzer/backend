from fastapi import FastAPI

from schemas import RegisterUser

app = FastAPI()


@app.post("/api/users/register")
async def register(new_user: RegisterUser):
    return {"User successfully registered": new_user.username}
