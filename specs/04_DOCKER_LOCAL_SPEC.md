# SPEC-04 — Docker y ejecución local

**ID:** SPEC-04  
**Prioridad:** P0

## 1. Objetivo

La aplicación completa debe arrancar localmente con:

```bash
docker compose up --build
```

## 2. Servicios

```yaml
services:
  backend:
    # FastAPI
  frontend:
    # Reflex
```

No incluir una base de datos en MVP sin necesidad funcional.

## 3. Puertos locales

- frontend: `3000`
- backend: `8000`

Accesos:

```text
http://localhost:3000
http://localhost:8000/docs
http://localhost:8000/health
```

## 4. Networking

- red Docker interna;
- frontend deberá resolver backend de forma apropiada;
- recordar que URL ejecutada desde el navegador debe ser públicamente alcanzable por el navegador;
- configurar URL API mediante entorno y no hardcodearla.

## 5. Dockerfile backend

Requisitos:

- imagen `python:<versión>-slim`;
- `WORKDIR`;
- instalar dependencias antes de copiar todo para aprovechar caché;
- copiar solo lo necesario;
- usuario no-root cuando sea viable;
- `PYTHONDONTWRITEBYTECODE=1`;
- `PYTHONUNBUFFERED=1`;
- healthcheck;
- `.dockerignore`.

## 6. Dockerfile frontend

Requisitos:

- build reproducible;
- variables de API;
- producción en modo optimizado;
- no depender de archivos del host;
- healthcheck.

## 7. Compose

Debe soportar:

```bash
docker compose up --build
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose down
```

## 8. Healthchecks

Backend:

```text
GET /health
```

Frontend:

- endpoint HTTP saludable o mecanismo recomendado por Reflex.

`depends_on` podrá usar condiciones de salud si son compatibles.

## 9. Variables

Crear `.env.example`, por ejemplo:

```env
APP_ENV=development
BACKEND_PUBLIC_URL=http://localhost:8000
FRONTEND_PUBLIC_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

No almacenar `.env` real en Git.

## 10. Volúmenes

En modo desarrollo se pueden montar fuentes para hot reload, pero la configuración de producción no dependerá de bind mounts.

## 11. Perfiles

Opcional:

```text
compose.yml
compose.dev.yml
```

Evitar duplicación innecesaria.

## 12. Criterios de aceptación

- [ ] clone limpio + `.env` desde example + compose levanta.
- [ ] frontend puede consultar backend.
- [ ] backend puede consultar proveedor externo.
- [ ] reiniciar contenedores no rompe configuración.
- [ ] logs aparecen por stdout/stderr.
- [ ] ningún secreto está dentro de la imagen.
