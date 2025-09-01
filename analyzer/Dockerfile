FROM python:3.11-slim

WORKDIR ..

COPY ./analyzer /analyzer
COPY ./util /util
COPY analyzer/main.py main.py

RUN pip install pip --upgrade
RUN pip install --no-cache-dir -r analyzer/requirements.txt
# We need to install CPU-only torch manually
RUN pip install torch==2.7.0+cpu --index-url https://download.pytorch.org/whl/cpu

ENTRYPOINT [ "python3", "main.py"]