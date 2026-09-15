#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${HOME}/Proyecto_Climatico"
REPO_URL="${REPO_URL:-https://github.com/JaqzO8/ProyectoClimaTEC.git}"
BRANCH="${BRANCH:-main}"

echo "=========================================="
echo "🚀 Iniciando despliegue en EC2 ClimaTEC"
echo "=========================================="

# 1. Asegurar Docker y Docker Compose instalados
if ! command -v docker &> /dev/null; then
    echo "📦 Docker no detectado. Instalando Docker..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -y
        sudo apt-get install -y ca-certificates curl gnupg lsb-release git
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes || true
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update -y
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    elif command -v dnf &> /dev/null || command -v yum &> /dev/null; then
        sudo dnf install -y docker git || sudo yum install -y docker git
        sudo systemctl enable --now docker
    fi
    sudo usermod -aG docker "$USER" || true
    echo "✅ Docker instalado exitosamente."
fi

# Iniciar servicio Docker si está detenido
sudo systemctl enable --now docker || true

# Instalar plugin buildx actualizado si es necesario
if ! docker buildx version 2>/dev/null | grep -q 'v0.2[0-9]'; then
    echo "📦 Actualizando docker-buildx..."
    sudo mkdir -p /usr/libexec/docker/cli-plugins /usr/local/lib/docker/cli-plugins
    sudo curl -sSL https://github.com/docker/buildx/releases/download/v0.21.2/buildx-v0.21.2.linux-amd64 -o /usr/libexec/docker/cli-plugins/docker-buildx
    sudo chmod +x /usr/libexec/docker/cli-plugins/docker-buildx
    sudo cp /usr/libexec/docker/cli-plugins/docker-buildx /usr/local/lib/docker/cli-plugins/docker-buildx
fi

# 2. Clonar o actualizar repositorio
if [ ! -d "$APP_DIR" ]; then
    echo "📥 Clonando repositorio desde $REPO_URL..."
    git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
else
    echo "🔄 Actualizando repositorio existente..."
    cd "$APP_DIR"
    git fetch origin "$BRANCH"
    git reset --hard "origin/$BRANCH"
fi

# 3. Detectar IP Pública de la instancia EC2 para configurar FRONTEND_PUBLIC_URL
EC2_PUBLIC_IP=$(curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4 || true)
if [ -z "$EC2_PUBLIC_IP" ]; then
    EC2_PUBLIC_IP=$(curl -s --connect-timeout 3 https://checkip.amazonaws.com || curl -s --connect-timeout 3 https://ifconfig.me || echo "localhost")
fi

PUBLIC_URL="${FRONTEND_PUBLIC_URL:-http://${EC2_PUBLIC_IP}:3000}"
echo "🌐 URL Pública configurada: $PUBLIC_URL"

# 4. Crear archivo .env de producción
cat <<EOF > .env
APP_ENV=production
FRONTEND_PUBLIC_URL=${PUBLIC_URL}
REFLEX_API_URL=${PUBLIC_URL}
BACKEND_HOST_PORT=8000
FRONTEND_HOST_PORT=3000
OPEN_METEO_API_MODE=free
WEATHER_TIMEOUT_SECONDS=5
WEATHER_CACHE_TTL_SECONDS=300
GEOCODING_CACHE_TTL_SECONDS=1800
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
CORS_ORIGINS=*
LOG_LEVEL=INFO
EOF

# 5. Construir y desplegar contenedores con Docker Compose
echo "🔨 Construyendo y levantando contenedores..."
sudo docker compose -f compose.prod.yml down --remove-orphans || true
sudo docker compose -f compose.prod.yml build --build-arg FRONTEND_PUBLIC_URL="${PUBLIC_URL}"
sudo docker compose -f compose.prod.yml up -d --remove-orphans

# 6. Esperar y verificar estado de los contenedores
echo "⏳ Esperando inicialización de servicios..."
sleep 15

echo "🔍 Estado de los contenedores:"
sudo $DOCKER_COMPOSE_CMD -f compose.prod.yml ps

# Limpieza de imágenes dangling
sudo docker image prune -f || true

echo "=========================================="
echo "🎉 ¡Despliegue finalizado exitosamente!"
echo "👉 Accede a la aplicación en: ${PUBLIC_URL}"
echo "=========================================="
