# Use a Python base image
FROM python:3.13-slim

ENV POLARS_TEMP_DIR=/tmp/polars

RUN mkdir -p /tmp/polars

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]