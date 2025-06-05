FROM python:3.11

WORKDIR ..

COPY ./scraper /scraper
COPY ./util /util

WORKDIR ./scraper

RUN pip install pip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]