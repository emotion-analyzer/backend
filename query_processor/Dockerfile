FROM python:3.11-slim

COPY ./query_processor /query_processor
COPY ./util /util

WORKDIR ./query_processor

RUN pip install pip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]