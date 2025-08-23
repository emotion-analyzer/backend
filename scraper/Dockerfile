FROM python:3.11-slim

WORKDIR ..

COPY ./scraper /scraper
COPY ./util /util
COPY scraper/main.py main.py

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r scraper/requirements.txt

ENTRYPOINT ["python3", "main.py"]