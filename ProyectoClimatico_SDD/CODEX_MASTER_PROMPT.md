# Prompt maestro para Codex — ProyectoClimatico

Quiero que construyas el proyecto completo **ProyectoClimatico** siguiendo estrictamente las especificaciones SDD incluidas en este repositorio.

## Fuente de verdad

Lee obligatoriamente y en orden:

1. `specs/00_MASTER_SPEC.md`
2. `specs/01_BACKEND_SPEC.md`
3. `specs/02_FRONTEND_SPEC.md`
4. `specs/03_WEATHER_DATA_SPEC.md`
5. `specs/04_DOCKER_LOCAL_SPEC.md`
6. `specs/05_AWS_TERRAFORM_SPEC.md`
7. `specs/06_GIT_CICD_SPEC.md`
8. `specs/07_QUALITY_SECURITY_SPEC.md`
9. `specs/08_ACCEPTANCE_GHERKIN.md`

Estas especificaciones son la fuente de verdad. No sustituyas tecnologías principales sin una razón técnica demostrable.

## Objetivo

Construye una aplicación web climática global que:

- esté desarrollada principalmente con Python;
- tenga backend FastAPI;
- tenga frontend Reflex;
- consulte clima actual y pronósticos;
- busque ubicaciones globalmente;
- represente correctamente país y niveles administrativos;
- use Open-Meteo mediante una interfaz de proveedor;
- tenga diseño claro/blanco, responsive y accesible;
- funcione con Docker local con sus respectivas configuraciones y en un puerto o con configuraciones con las cuales no estoy usando.
- tenga infraestructura Terraform para AWS;
- esté preparada para Git con repo `ProyectoClimatico`;
- tenga CI/CD;
- tenga pruebas automatizadas y métricas de calidad.

## Modo de ejecución

Trabaja por fases y no saltes las validaciones.

### Fase 1 — Bootstrap

1. Verifica la estructura.
2. Crea los archivos base.
3. Inicializa Git solo si no existe.
4. Asegura que la raíz corresponda al repo `ProyectoClimatico`.
5. Crea `.gitignore`, `.editorconfig`, `.env.example`.
6. No inventes un remote Git.

Validación:

- estructura consistente;
- no secrets.

### Fase 2 — Backend

Implementa:

- configuración;
- dominio;
- provider port;
- adapter Open-Meteo;
- location search;
- current;
- hourly;
- daily;
- overview;
- error model;
- logging;
- cache;
- tests.

Validación:

```bash
ruff check backend
mypy backend
pytest backend
```

Corrige antes de continuar.

### Fase 3 — Frontend

Implementa la UI conforme a SPEC-02.

Debe tener:

- buscador;
- geolocalización;
- clima actual;
- hourly;
- daily;
- mapa;
- unidades;
- loading/error/empty;
- responsive;
- accesibilidad.

No reemplaces la base blanca con un diseño oscuro.

Valida imports, ejecución y tests.

### Fase 4 — Integración

Integra frontend con `/api/v1`.

Prueba:

- búsquedas;
- selección;
- unidades;
- error;
- timeout;
- geolocalización rechazada.

### Fase 5 — Docker

Crea imágenes y Compose.

Ejecuta:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Verifica healthchecks y realiza smoke test HTTP.

Si el entorno de ejecución no permite Docker, documenta exactamente qué comando no pudo ejecutarse, pero deja los archivos válidos.

### Fase 6 — Quality gates

Ejecuta:

- lint;
- formatter check;
- mypy;
- tests;
- coverage;
- mutation testing base;
- secret/dependency checks disponibles.

No ocultes pruebas fallidas.

### Fase 7 — Terraform AWS

Implementa IaC para:

- ECR;
- ECS/Fargate;
- ALB;
- networking;
- IAM;
- CloudWatch.

Ejecuta al menos:

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

No realices `terraform apply` sin tener una cuenta/región/credenciales AWS válidas y autorización.

### Fase 8 — GitHub Actions

Crear:

- CI;
- Docker build;
- AWS deploy.

AWS debe autenticarse por OIDC.

No inventes ARN de roles, account IDs, Git URLs o dominios.

Usa placeholders/configuración explícita.

### Fase 9 — Documentación final

README debe incluir:

- arquitectura;
- stack;
- requisitos;
- instalación sin Docker si aplica;
- instalación con Docker;
- variables;
- tests;
- endpoints;
- Terraform;
- AWS;
- Git remote;
- CI/CD;
- troubleshooting.

## Reglas de ingeniería

- Código legible y tipado.
- Funciones pequeñas.
- No duplicación injustificada.
- No God classes.
- No secretos.
- No catch-all silenciosos.
- No `except Exception: pass`.
- No datos meteorológicos fake en producción.
- Fixtures fake sí están permitidas en tests.
- No llamadas de proveedor directas desde UI.
- No acoplar casos de uso a Open-Meteo.
- No afirmar “observación en tiempo real” si el proveedor entrega condición modelada/actual.
- No guardar ubicación precisa del usuario en servidor.
- No agregar base de datos al MVP sin requisito real.
- No agregar autenticación al MVP sin requisito real.

## Política de decisiones

Si una ambigüedad menor puede resolverse de forma razonable y consistente con los specs, resuélvela y documenta la decisión.

Solo requiere entrada externa cuando sea imposible continuar sin un dato real, por ejemplo:

- URL del repositorio remoto;
- AWS account/role;
- dominio real;
- credenciales/configuración autorizada.

En esos casos deja la implementación preparada con placeholders y continúa con todo lo demás.

## Entrega final esperada

Al terminar presenta:

1. resumen de lo implementado;
2. árbol de archivos;
3. comandos exactos para ejecutar local;
4. URLs locales;
5. resultado de pruebas;
6. cobertura;
7. resultado de Docker;
8. resultado de Terraform validate;
9. variables pendientes para AWS;
10. comando para añadir el remote Git;
11. pendientes reales, si existen.

No declares una validación como exitosa si no la ejecutaste.
