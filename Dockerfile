FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/ingestion

WORKDIR /app

# unstructured[pdf] can poppler/tesseract/libmagic
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential poppler-utils tesseract-ocr libmagic1 libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs
