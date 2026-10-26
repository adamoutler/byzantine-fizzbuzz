# Multi-stage security-hardened Dockerfile for Byzantine FizzBuzz Live
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim-bookworm AS runner

# Security hardening: create unprivileged system account
RUN groupadd -r byzantine && useradd -r -g byzantine -u 10001 byzantine \
    && mkdir -p /app /data && chown -R byzantine:byzantine /app /data

WORKDIR /app
COPY --from=builder /root/.local /home/byzantine/.local
COPY ./app /app/app
COPY ./requirements.txt /app/

ENV PATH=/home/byzantine/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_PATH=/data/dockets.db

USER byzantine

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
