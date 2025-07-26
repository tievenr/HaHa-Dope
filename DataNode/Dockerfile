FROM python:3.12-slim

WORKDIR /usr/local/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl

COPY src/ ./src

