# ProyectoClimatico

Aplicación web global para consultar clima actual y pronósticos meteorológicos de ubicaciones de cualquier país, construida con **Python** (FastAPI en el backend y Reflex en el frontend).

---

## Arquitectura del sistema

```text
Browser / Client (HTML/JS)
         |
         v
Frontend Reflex (Port 3000)
         |
         | HTTPS / API REST
         v
FastAPI Backend (Port 8000)
         |
         +--> Application Services / Use Cases
         |
         +--> WeatherProvider Protocol
                 |
                 +--> OpenMeteoWeatherProvider (Adapter)
```

### Capas Clean Architecture (Backend)
- `domain`: Modelos Pydantic v2, enums de unidades, catálogo de WMO codes.
- `application`: Puerto `WeatherProvider` y casos de uso (`SearchLocations`, `GetCurrentWeather`, `GetHourlyForecast`, `GetDailyForecast`, `GetWeatherOverview`).
- `infrastructure`: Adaptador de Open-Meteo API, caché TTL en memoria (`TTLMemoryCache`), estructuración de logs JSON (`structlog`), configuración `pydantic-settings`.
- `api/v1`: Controladores FastAPI, documentación OpenAPI/Swagger, middleware de seguridad y normalización de respuestas de error.

---

## Stack tecnológico

- **Lenguaje principal**: Python 3.11+ / 3.13+
- **Backend Framework**: FastAPI
- **Frontend Framework**: Reflex (Python UI)
- **Cliente HTTP Async**: HTTPX
- **Proveedor Meteorológico**: Open-Meteo API (Geocoding & Forecast)
- **Caché**: TTL Memory Cache (`cachetools`)
- **Contenedores**: Docker & Docker Compose
- **IaC (Infraestructura como código)**: Terraform (AWS ECS Fargate, ALB, ECR, IAM, CloudWatch)
- **CI/CD**: GitHub Actions (OIDC Auth para AWS, Docker build/push, Quality Gates)

---

## Requisitos previos

- Python 3.11+ (para ejecución directa sin Docker)
- Docker & Docker Compose (para ejecución en contenedores)
- Terraform 1.5+ (para despliegue en AWS)

---

## Variables de entorno

Copia `.env.example` a `.env`:

```env
APP_ENV=development
APP_NAME=ProyectoClimatico
API_V1_PREFIX=/api/v1
WEATHER_PROVIDER=open_meteo
WEATHER_TIMEOUT_SECONDS=5
WEATHER_CACHE_TTL_SECONDS=300
GEOCODING_CACHE_TTL_SECONDS=1800
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=INFO
BACKEND_PUBLIC_URL=http://localhost:8000
FRONTEND_PUBLIC_URL=http://localhost:3000
```

---

## Instalación y ejecución local

### Opción 1: Con Docker Compose (Recomendado)

```bash
# Levantar el stack completo
docker compose up --build -d

# Verificar estado de salud de los contenedores
docker compose ps

# Ver logs
docker compose logs -f backend
docker compose logs -f frontend

# Detener los contenedores
docker compose down
```

- **Frontend UI**: [http://localhost:3000](http://localhost:3000)
- **Backend OpenAPI/Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Healthcheck**: [http://localhost:8000/health](http://localhost:8000/health)

### Opción 2: Sin Docker (Ejecución directa)

1. **Backend**:
   ```bash
   cd backend
   python -m pip install -r pyproject.toml .[dev]
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   python -m pip install -r pyproject.toml .[dev]
   reflex run --frontend-port 3000
   ```

---

## Pruebas automatizadas y calidad de código

```bash
# Formateador y Linter
python -m ruff check backend frontend
python -m ruff format --check backend frontend

# Verificación de tipos estáticos
python -m mypy app

# Pruebas Backend con reporte de cobertura
python -m pytest backend/tests --cov=app --cov-report=term-missing

# Pruebas Frontend
python -m pytest frontend/tests
```

---

## Endpoints de la API Backend

- `GET /health`: Estado de salud básico del backend.
- `GET /ready`: Verificación de preparación del servicio.
- `GET /api/v1/locations/search?q={query}&limit=10`: Búsqueda global de lugares con desambiguación jerárquica (`admin1`..`admin4`, país).
- `GET /api/v1/weather/current?latitude={lat}&longitude={lon}`: Condiciones meteorológicas actuales.
- `GET /api/v1/weather/hourly?latitude={lat}&longitude={lon}&hours=24`: Pronóstico por horas.
- `GET /api/v1/weather/daily?latitude={lat}&longitude={lon}&days=7`: Pronóstico diario.
- `GET /api/v1/weather/overview?latitude={lat}&longitude={lon}`: Resumen climático completo (current + 24h + 7d).

---

## Infraestructura en AWS con Terraform

La configuración de Terraform se encuentra en `infra/terraform/`:

```text
infra/terraform/
├─ modules/
│  ├─ network/       # VPC, Subnets públicas multi-AZ, Internet Gateway, Security Groups
│  ├─ ecr/           # Repositorios ECR para backend y frontend con escaneo de imágenes
│  ├─ alb/           # Application Load Balancer y Target Groups (/api/* -> backend, /* -> frontend)
│  ├─ ecs/           # Cluster ECS Fargate, Task Definitions y Servicios
│  ├─ iam/           # Roles de ejecución de tareas y rol OIDC para GitHub Actions
│  └─ observability/ # Log Groups de CloudWatch
└─ envs/
   ├─ dev/           # Entorno de desarrollo
   └─ prod/          # Entorno de producción
```

### Comandos de validación IaC

```bash
# Validar sintaxis y formato de Terraform
terraform fmt -check -recursive infra/terraform

# Inicializar y validar módulo dev
cd infra/terraform/envs/dev
terraform init -backend=false
terraform validate
```

---

## Git y CI/CD en GitHub Actions

### Configuración del repositorio remoto

```bash
git remote add origin <GIT_REMOTE_URL>
git push -u origin main
```

### Workflows en `.github/workflows/`

1. `ci.yml`: Ejecuta `ruff`, `mypy`, `pytest` backend/frontend, prueba de cobertura y validación de Terraform en cada `pull_request` y `push` a `main`.
2. `docker.yml`: Construye y valida las imágenes Docker de backend y frontend.
3. `deploy-aws.yml`: Autenticación AWS por OIDC, login en ECR, compilación y tagging de imágenes por SHA de Git, push a ECR y actualización del servicio en ECS Fargate.

---

## Licencia

Este proyecto está bajo la Licencia [MIT](LICENSE).
