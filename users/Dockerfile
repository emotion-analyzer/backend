FROM python:3.11

WORKDIR /users

COPY . /users

RUN pip install pip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "fastapi", "run", "--host", "0.0.0.0", "--port", "8001"]