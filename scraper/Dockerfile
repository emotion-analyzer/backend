FROM python:3.11-slim

WORKDIR /app

COPY ./scraper /app/scraper
COPY ./util /app/util

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r scraper/requirements.txt

WORKDIR /app

ENTRYPOINT ["python3", "-m", "scraper.main"]