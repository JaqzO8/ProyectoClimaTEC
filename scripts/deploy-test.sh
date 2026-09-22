#!/usr/bin/env bash
set -eo pipefail

TARGET_HOST="${1:-}"
MAX_RETRIES="${2:-10}"
DELAY="${3:-10}"

if [ -z "$TARGET_HOST" ]; then
  echo "Uso: $0 <IP_O_DNS_DEL_SERVIDOR> [MAX_RETRIES] [DELAY]"
  exit 1
fi

echo "=================================================="
echo "    PROYECTOCLIMATICO - TEST DE DISPONIBILIDAD HTTP"
echo "=================================================="
echo "Host objetivo: http://$TARGET_HOST"
echo "Intentos máximos: $MAX_RETRIES | Intervalo: ${DELAY}s"
echo "=================================================="

SUCCESS=false

for ((i=1; i<=MAX_RETRIES; i++)); do
  echo "--> Intento $i/$MAX_RETRIES: verificando endpoint..."
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://$TARGET_HOST/health" || echo "000")
  
  if [ "$HTTP_CODE" -eq 200 ]; then
    echo " [OK] Endpoint respondió con HTTP 200"
    SUCCESS=true
    break
  else
    echo " [Esperando] Endpoint devolvió HTTP $HTTP_CODE. Reintentando en ${DELAY}s..."
    sleep "$DELAY"
  fi
done

if [ "$SUCCESS" = false ]; then
  echo " [ERROR] El servidor no respondió con HTTP 200 tras $MAX_RETRIES intentos."
  exit 1
fi

echo ""
echo "=================================================="
echo "    DEPLOYMENT VALIDATION: PASSED                 "
echo "=================================================="
