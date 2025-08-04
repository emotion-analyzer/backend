FROM python:3.11-slim

WORKDIR /app

COPY ./analyzer /app/analyzer
COPY ./util /app/util

RUN pip install pip --upgrade
RUN pip install --no-cache-dir -r analyzer/requirements.txt
# We need to install CPU-only torch manually
RUN pip install torch==2.7.0+cpu --index-url https://download.pytorch.org/whl/cpu

WORKDIR /app

ENTRYPOINT [ "python3", "-m", "analyzer.main"]