FROM python:3.13-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    unzip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml rxconfig.py ./
RUN pip install --no-cache-dir .

COPY proyecto_climatico ./proyecto_climatico

FROM python:3.13-slim as runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=3000

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/sh appuser && \
    mkdir -p /home/appuser/.local /app && \
    chown -R appuser:appgroup /home/appuser /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder --chown=appuser:appgroup /app /app

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000')" || exit 1

CMD ["reflex", "run", "--env", "prod", "--frontend-port", "3000"]
