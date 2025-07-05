FROM python:3.10-slim

WORKDIR /app

COPY . /app
COPY wait-for-it.sh /wait-for-it.sh

RUN pip install --upgrade pip && pip install -r requirements.txt
RUN chmod +x /wait-for-it.sh
RUN apt-get update && apt-get install -y netcat-openbsd curl

ENV PYTHONPATH=/app

EXPOSE 8002
EXPOSE 8501

CMD ["/wait-for-it.sh", "-h", "postgres", "-p", "5432", "--", "uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8002"]