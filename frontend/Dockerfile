FROM python:3.13-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 REFLEX_TELEMETRY_ENABLED=false
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.lock .
RUN pip install --no-cache-dir --require-hashes -r requirements.lock
COPY rxconfig.py serve.py ./
COPY reflex.lock ./reflex.lock
COPY proyecto_climatico ./proyecto_climatico
ARG FRONTEND_PUBLIC_URL=http://localhost:3000
ENV REFLEX_API_URL=$FRONTEND_PUBLIC_URL FRONTEND_PUBLIC_URL=$FRONTEND_PUBLIC_URL
RUN reflex init && reflex export --frontend-only --no-zip
RUN if [ -f /root/.local/share/reflex/bun/bin/bun ]; then cp /root/.local/share/reflex/bun/bin/bun /usr/local/bin/bun; fi

FROM python:3.13-slim AS runner
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 REFLEX_TELEMETRY_ENABLED=false \
    REFLEX_SKIP_COMPILE=true REFLEX_ENV_MODE=prod GRANIAN_WORKERS=1 PATH="/home/appuser/.local/share/reflex/bun/bin:${PATH}"
RUN groupadd -g 1000 appgroup && useradd -u 1000 -g appgroup -m -s /bin/sh appuser
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local
COPY --from=builder --chown=appuser:appgroup /app /app
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/ping', timeout=3); urllib.request.urlopen('http://localhost:3000/', timeout=3)"
CMD ["python", "serve.py"]
