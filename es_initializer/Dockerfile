FROM python:3.11-slim

WORKDIR ..

COPY ./es_initializer /es_initializer
COPY ./util /util
COPY es_initializer/main.py main.py

RUN pip install pip --upgrade
RUN pip install --no-cache-dir -r es_initializer/requirements.txt

ENTRYPOINT [ "python3", "main.py"]