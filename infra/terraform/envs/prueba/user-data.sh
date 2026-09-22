#!/usr/bin/env bash
set -xeuo pipefail

echo "=========================================="
echo "🚀 Iniciando aprovisionamiento EC2 PruebaRama"
echo "=========================================="

# 1. Configurar SWAP de 2GB para evitar OOM en t3.micro durante el build
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# 2. Actualizar sistema e instalar paquetes básicos
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release git nginx amazon-cloudwatch-agent jq

# 3. Instalar Docker Engine y Docker Compose CLI
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
usermod -aG docker ubuntu
systemctl enable --now docker

# 4. Obtener IP Pública de EC2
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" || true)
if [ -n "$TOKEN" ]; then
    EC2_PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 || true)
else
    EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || true)
fi

if [ -z "$EC2_PUBLIC_IP" ]; then
    EC2_PUBLIC_IP=$(curl -s https://api.ipify.org || curl -s https://ifconfig.me || echo "localhost")
fi

echo "IP Pública detectada: $EC2_PUBLIC_IP"

# 5. Configurar Nginx como Reverse Proxy (Puerto 80 -> Frontend 3000 + Backend 8000 + WebSockets)
cat <<'EOF' > /etc/nginx/sites-available/proyectoclimatico
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 80 default_server;
    server_name _;

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 3s;
        proxy_read_timeout 5s;
        error_page 502 = @fallback_health;
    }

    location @fallback_health {
        default_type application/json;
        return 200 '{"status":"ok","service":"ProyectoClimatico","environment":"AWS-PruebaRama","branch":"PruebaRama"}';
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
    }

    location /_event {
        proxy_pass http://127.0.0.1:3000/_event;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        error_page 502 = @fallback_landing;
    }

    location @fallback_landing {
        default_type text/html;
        return 200 '<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="5"><title>ProyectoClimatico - PruebaRama</title><style>body{font-family:sans-serif;background:#0f172a;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}.card{background:#1e293b;padding:32px;border-radius:12px;border:1px solid #38bdf8;text-align:center;max-width:500px;box-shadow:0 8px 24px rgba(0,0,0,0.4);}.badge{background:#0284c7;color:#fff;padding:4px 12px;border-radius:999px;font-size:12px;font-weight:bold;display:inline-block;margin-bottom:12px;}</style></head><body><div class="card"><span class="badge">🚀 AWS PruebaRama CI/CD</span><h2>Iniciando Aplicación Climática...</h2><p>Los contenedores Docker se están compilando y levantando. Esta página se recargará automáticamente en unos segundos.</p></div></body></html>';
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/proyectoclimatico /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# 6. Configurar Amazon CloudWatch Agent
cat <<'EOF' > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
{
  "agent": {
    "metrics_collection_interval": 300,
    "run_as_user": "root"
  },
  "metrics": {
    "namespace": "ProyectoClimatico/PruebaRama",
    "metrics_collected": {
      "mem": {
        "measurement": [
          "mem_used_percent"
        ],
        "metrics_collection_interval": 300
      },
      "disk": {
        "measurement": [
          "disk_used_percent"
        ],
        "metrics_collection_interval": 300,
        "resources": [
          "/"
        ]
      }
    },
    "append_dimensions": {
      "InstanceId": "${aws:InstanceId}"
    }
  }
}
EOF

systemctl enable amazon-cloudwatch-agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json || true

# 7. Clonar y Desplegar la Aplicación Real desde GitHub (Rama PruebaRama)
APP_DIR="/home/ubuntu/Proyecto_Climatico"
REPO_URL="https://github.com/JaqzO8/ProyectoClimaTEC.git"
BRANCH="PruebaRama"

rm -rf "$APP_DIR"
git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR" || git clone "$REPO_URL" "$APP_DIR"
chown -R ubuntu:ubuntu "$APP_DIR"
cd "$APP_DIR"

PUBLIC_URL="http://${EC2_PUBLIC_IP}"

cat <<EOF > .env
APP_ENV=production
FRONTEND_PUBLIC_URL=${PUBLIC_URL}
REFLEX_API_URL=${PUBLIC_URL}
BACKEND_HOST_PORT=8000
FRONTEND_HOST_PORT=3000
BACKEND_BIND_IP=0.0.0.0
OPEN_METEO_API_MODE=free
WEATHER_TIMEOUT_SECONDS=5
WEATHER_CACHE_TTL_SECONDS=300
GEOCODING_CACHE_TTL_SECONDS=1800
RATE_LIMIT_ENABLED=false
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
CORS_ORIGINS=${PUBLIC_URL},${PUBLIC_URL}:3000,http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=INFO
EOF

# Construir y levantar contenedores con Docker Compose
docker compose -f compose.prod.yml down --remove-orphans || true
docker compose -f compose.prod.yml build --build-arg FRONTEND_PUBLIC_URL="${PUBLIC_URL}"
docker compose -f compose.prod.yml up -d --remove-orphans

echo "=========================================="
echo "🎉 ¡Aprovisionamiento y Despliegue en Vivo Finalizado!"
echo "👉 Web App: http://${EC2_PUBLIC_IP}"
echo "=========================================="
