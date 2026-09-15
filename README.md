# ProyectoClimatico

Aplicación meteorológica en Python 3.13: **FastAPI + Reflex + Open-Meteo**.
Infraestructura AWS con Terraform (ECS Fargate, ECR, ALB, IAM y CloudWatch).

## Ejecutar con Docker

```bash
cp .env.example .env
docker compose up --build --wait
```

En PowerShell, usa `Copy-Item .env.example .env`.

- Interfaz: http://localhost:3000
- API y documentación: http://localhost:8000/docs
- Salud: http://localhost:8000/health
- Estado: `docker compose ps`
- Detener: `docker compose down`

Los puertos del host se pueden cambiar en `.env` mediante `FRONTEND_HOST_PORT` y
`BACKEND_HOST_PORT`. Si cambias el puerto de la interfaz, actualiza también
`FRONTEND_PUBLIC_URL` y `CORS_ORIGINS`, y reconstruye el frontend.

## Clave de Open-Meteo

Configura en tu archivo **local** `.env`:

```dotenv
OPEN_METEO_API_MODE=commercial
OPEN_METEO_API_KEY=
```

Completa el valor vacío únicamente en tu archivo local. En AWS, guarda la clave
como texto plano en **Secrets Manager** y configura su **ARN** en Terraform y
GitHub; nunca copies su valor al código, a variables del frontend o a argumentos
de Docker. El backend elige los endpoints `customer-*` en modo comercial.

El modo `free` funciona sin clave para los usos admitidos por Open-Meteo.
Una suscripción proporciona la clave y licencia comercial:
[planes de Open-Meteo](https://open-meteo.com/en/pricing) y
[documentación del parámetro apikey](https://open-meteo.com/en/docs).

## Desarrollo sin Docker

Crea y activa un entorno virtual Python 3.13. Instala desde la raíz:

```bash
python -m pip install --require-hashes -r backend/requirements-dev.lock
python -m pip install --require-hashes -r frontend/requirements-dev.lock
python -m pip install --no-deps -e backend -e frontend
```

Backend, en una terminal:

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Frontend, en otra terminal:

```bash
cd frontend
reflex run --env prod --frontend-port 3000 --backend-port 3000
```

El backend lee `.env` desde el directorio de ejecución; para ejecución directa
colócalo en `backend/.env`, o exporta las variables al proceso. Compose lee el
`.env` de la raíz. Ninguno se versiona.

## Arquitectura

```text
Navegador → Reflex (3000: HTML, eventos y WebSocket)
                  ↓ BACKEND_INTERNAL_URL
           FastAPI (8000: /api/v1)
                  ↓ WeatherProvider
           Adaptador Open-Meteo → API externa
```

- `backend/app/domain`: modelos y catálogo WMO.
- `backend/app/application`: interfaz del proveedor y casos de uso.
- `backend/app/infrastructure`: HTTP asíncrono, caché TTL, logs y límites.
- `frontend/proyecto_climatico`: componentes, estado y cliente de la API propia.
- `infra/terraform/envs/{dev,prod}`: entornos de AWS.
- `scripts`: controles de repositorio, despliegue y validación.
- `tests/e2e`: navegador con proveedor simulado, exclusivo de pruebas.
- `specs`: especificaciones SDD.

Reflex publica la UI y sus eventos por el mismo puerto. En AWS, el ALB envía
`/api/*`, salud y documentación a FastAPI; el resto, incluidos `/_event` y
`/ping`, a Reflex. Las preferencias de unidades usan almacenamiento local del
navegador; el estado de sesión de Reflex se mantiene en memoria y usa afinidad
de sesión en el ALB. Un reinicio puede reiniciar la selección.

## Pruebas y calidad

```bash
python -m ruff check backend frontend scripts tests/e2e
python -m ruff format --check backend frontend scripts tests/e2e
python -m mypy --config-file backend/pyproject.toml backend/app
python -m mypy --config-file frontend/pyproject.toml frontend/proyecto_climatico frontend/rxconfig.py frontend/serve.py
python -m pytest backend/tests --cov=app --cov-report=term-missing --cov-fail-under=85
python -m pytest frontend/tests --cov=proyecto_climatico.state --cov=proyecto_climatico.services --cov-fail-under=80
python scripts/mutation_smoke.py
python scripts/check_repository.py
python -m pip_audit --disable-pip -r backend/requirements.lock
python -m pip_audit --disable-pip -r frontend/requirements.lock
```

El control de dominio/aplicación exige 90 % de cobertura en CI.
La suite base de mutaciones comprueba ocho alteraciones aisladas (objetivo 70 %).
Para análisis más amplio en Linux/WSL: `cd backend && mutmut run`.

Pruebas de navegador:

```bash
docker compose -f compose.yml -f tests/e2e/compose.test.yml up --build --wait
python -m pip install -r tests/e2e/requirements.txt
python -m playwright install chromium
python -m pytest tests/e2e -v
docker compose down
```

El override de pruebas sustituye solamente el proveedor externo; no se incorpora
a las imágenes de producción.

## GitHub Actions y producción

[Guía de AWS, Secrets Manager, OIDC, arranque y rollback](docs/DEPLOYMENT.md).

- **CI Quality Gates**: formato, Ruff, mypy, pytest, cobertura, mutaciones, auditoría
  de dependencias, Gitleaks del historial completo, actionlint, Terraform dev/prod
  y Docker con pruebas de navegador.
- **Docker Image Build Validation**: workflow reutilizable invocado por CI.
- **Deploy to AWS ECS**: solo después de CI exitoso del commit de `main`; OIDC,
  ECR por SHA, nuevas task definitions, espera de estabilidad, verificación de
  revisiones y pruebas HTTP. Restaura las revisiones anteriores si falla el rollout.
- Sin configuración AWS real, la ejecución automática informa **despliegue
  pendiente** y omite la publicación. Una ejecución manual incompleta falla con
  los nombres de las variables faltantes.

Usamos el remoto existente:
[github.com/JaqzO8/ProyectoClimaTEC](https://github.com/JaqzO8/ProyectoClimaTEC).
Las especificaciones llaman al producto ProyectoClimatico; no se renombra el
repositorio existente. Trabaja con ramas cortas, PRs y commits convencionales.

## Protección de credenciales

`.gitignore` excluye `.env` y variantes, claves privadas, credenciales locales,
`*.tfvars`, planes y estados de Terraform. Solo se permiten plantillas
`*.example` sin valores secretos. Los lockfiles de dependencias sí se versionan.

Cada contexto Docker tiene una lista explícita de archivos permitidos. No se
copia el repositorio completo a las imágenes. Los logs HTTP omiten query strings
y los errores públicos no exponen excepciones del proveedor.

Antes de publicar:

```bash
git diff --cached --check
python scripts/check_repository.py
gitleaks git --redact --log-opts="--all" .
```

Si alguna vez se publica una clave, revócala primero; agregarla a `.gitignore`
no la elimina del historial.

## API

- `GET /health`, `GET /ready`
- `GET /api/v1/locations/search?q=Lima`
- `GET /api/v1/weather/current?latitude=-12.04&longitude=-77.03`
- `GET /api/v1/weather/hourly?latitude=-12.04&longitude=-77.03&hours=24`
- `GET /api/v1/weather/daily?latitude=-12.04&longitude=-77.03&days=7`
- `GET /api/v1/weather/overview?latitude=-12.04&longitude=-77.03`

Temperatura: `celsius|fahrenheit`; viento: `kmh|ms|mph`;
precipitación: `mm|inch`. Los datos llevan la zona horaria del lugar.

## Diagnóstico

- Docker sin motor: inicia Docker Desktop con contenedores Linux y comprueba `docker info`.
- UI sin conexión: `REFLEX_API_URL` debe ser la URL pública de Reflex; la conexión
  meteorológica desde su servidor usa `BACKEND_INTERNAL_URL`.
- Clave rechazada: revisa modo comercial, suscripción y valor de Secrets Manager.
  Rotar el secreto requiere desplegar nuevas tareas ECS.
- Geolocalización: el navegador exige HTTPS o localhost. Rechazar el permiso
  mantiene disponible el buscador. El mapa externo se desactiva al usar geolocalización.
- Rate limiting: por proceso, 120 solicitudes/minuto por defecto. Solo activa
  `TRUST_ALB_HEADERS=true` detrás del ALB con ingreso restringido por security groups;
  interpreta la última dirección añadida por ALB en modo append.
- Falta de datos meteorológicos: el backend devuelve un error normalizado;
  nunca sustituye mediciones ausentes por clima inventado.

Licencia del código: [MIT](LICENSE).
