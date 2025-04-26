from fastapi import FastAPI

app = FastAPI()


@app.get("/hello_world")
async def root():
    return {"message": "Hello World"}