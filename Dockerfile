FROM python:3.12-slim

# copy san binary uv, khong can pip install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/ingestion \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# layer dependency: chi build lai khi requirements.txt doi
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r requirements.txt

# layer code: doi code chi build lai tu day
COPY . .

RUN mkdir -p logs
