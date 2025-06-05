FROM python:3.11-slim

WORKDIR ..

COPY ./users /users
COPY ./util /util

WORKDIR ./users

RUN pip install pip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]