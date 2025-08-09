FROM python:3.12-slim

WORKDIR /usr/local/app/src

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl

COPY src/ ./

EXPOSE 9870


CMD ["python", "-u", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9870"]