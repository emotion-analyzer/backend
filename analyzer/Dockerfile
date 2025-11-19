FROM python:3.11-slim

WORKDIR ..

COPY ./analyzer /analyzer
COPY ./util /util
COPY analyzer/main.py main.py

RUN pip install pip --upgrade
RUN pip install --no-cache-dir -r analyzer/requirements.txt

ENTRYPOINT [ "python3", "main.py"]