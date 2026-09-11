# SPEC-06 — Git y CI/CD

**ID:** SPEC-06  
**Prioridad:** P0

## 1. Repositorio

Nombre obligatorio:

```text
ProyectoClimatico
```

Inicialización:

```bash
mkdir ProyectoClimatico
cd ProyectoClimatico
git init
git branch -M main
```

Si la carpeta ya existe, no recrearla destructivamente.

## 2. Remote

El usuario deberá proporcionar el remote real.

Codex NO debe inventar organización, usuario ni URL.

Cuando se proporcione:

```bash
git remote add origin <GIT_REMOTE_URL>
git push -u origin main
```

Si `origin` ya existe:

```bash
git remote -v
```

y actualizar solo si el usuario lo autorizó.

## 3. Branching

Mínimo:

```text
main
feature/<descripcion>
fix/<descripcion>
chore/<descripcion>
```

Para proyecto individual se permite trunk-based con ramas cortas.

## 4. Commits

Conventional Commits:

```text
feat:
fix:
docs:
test:
refactor:
chore:
ci:
build:
```

Ejemplos:

```text
feat(backend): add global location search
feat(frontend): add current weather dashboard
chore(docker): add local compose stack
ci(aws): deploy images to ECS
```

## 5. .gitignore

Debe incluir:

- `.env`
- `.venv`
- `__pycache__`
- `.pytest_cache`
- `.mypy_cache`
- `.ruff_cache`
- coverage
- Reflex build/cache
- Terraform `.terraform`
- `*.tfstate*`
- IDE local
- OS junk.

## 6. Pull request checks

Obligatorios:

- Ruff;
- format check;
- mypy;
- backend tests;
- frontend tests;
- coverage;
- Docker build;
- Terraform fmt/validate;
- secret scan;
- dependency audit recomendado.

## 7. Workflows

Crear:

```text
.github/workflows/ci.yml
.github/workflows/docker.yml
.github/workflows/deploy-aws.yml
```

### `ci.yml`

Triggers:

- pull_request;
- push main.

### `docker.yml`

Build de ambas imágenes para comprobar reproducibilidad.

### `deploy-aws.yml`

Trigger recomendado:

- push a `main`;
- o workflow_dispatch para entorno dev/prod.

## 8. AWS Auth

Usar OIDC.

Workflow requerirá:

```yaml
permissions:
  id-token: write
  contents: read
```

El role AWS debe restringirse al repositorio/rama/environment correspondiente.

No guardar `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` de larga duración como diseño normal.

## 9. Tags Docker

Siempre:

```text
<git-sha>
```

Opcional:

```text
latest
dev
vX.Y.Z
```

El deployment debe usar tag inmutable (SHA) cuando sea posible.

## 10. Entornos GitHub

Recomendado:

- `development`;
- `production`.

Production podrá requerir approval manual.

## 11. Release

SemVer:

```text
0.1.0 MVP
0.2.0 mejoras
1.0.0 release estable
```

## 12. Criterios de aceptación

- [ ] repo se llama ProyectoClimatico.
- [ ] main protegible.
- [ ] CI falla si tests/lint fallan.
- [ ] imágenes construyen.
- [ ] deploy usa OIDC.
- [ ] no hay credenciales AWS permanentes en repo.
- [ ] README explica cómo definir remote.
