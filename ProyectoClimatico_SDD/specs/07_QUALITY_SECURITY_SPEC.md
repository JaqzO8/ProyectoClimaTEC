# SPEC-07 — Calidad, pruebas, seguridad y observabilidad

**ID:** SPEC-07  
**Prioridad:** P0

## 1. Herramientas

Backend/frontend Python:

- Ruff;
- mypy;
- pytest;
- pytest-asyncio;
- coverage.py / pytest-cov;
- Hypothesis;
- mutation testing con `mutmut` o equivalente compatible.

Seguridad:

- pip-audit o equivalente;
- secret scanning;
- Docker image scanning recomendado.

## 2. Métricas objetivo

Cobertura inicial:

```text
domain/application: >= 90%
backend total:      >= 85%
frontend logic:     >= 80%
project total:      >= 80%
```

No perseguir cobertura mediante tests vacíos.

## 3. Mutation testing

Aplicar inicialmente a:

- mapeo WMO;
- validaciones;
- conversiones;
- reglas de formato;
- casos de uso.

Meta inicial orientativa:

```text
mutation score >= 70%
```

Subir progresivamente.

## 4. Pirámide de pruebas

```text
        E2E
      integración
    unitarias
```

Priorizar unitarias.

E2E solo para flujos críticos.

## 5. E2E críticos

1. abrir home;
2. buscar una ciudad;
3. seleccionar resultado;
4. ver current;
5. ver hourly;
6. ver daily;
7. cambiar unidades;
8. simular error de API;
9. móvil.

No depender de red climática real en CI si puede evitarse.

## 6. Quality gates

PR no mergeable si falla:

- format;
- lint;
- typecheck;
- test;
- cobertura;
- Docker build;
- Terraform validate.

## 7. OWASP

Aplicar principios OWASP relevantes:

- input validation;
- output encoding;
- dependency hygiene;
- secure headers;
- least privilege;
- logging seguro;
- rate limiting;
- evitar SSRF: el usuario nunca elige URL arbitraria de proveedor;
- evitar secretos en logs.

## 8. Protección de API

- parámetros tipados;
- límites de `q` y `limit`;
- rate limit por IP/configuración;
- timeout externo;
- no proxy genérico;
- no aceptar URL meteorológica del cliente;
- CORS allowlist.

## 9. Logs estructurados

Campos recomendados:

```text
timestamp
level
service
environment
request_id
path
method
status_code
duration_ms
provider
provider_duration_ms
cache_hit
```

No loggear coordenadas exactas de geolocalización como práctica normal en producción si no son necesarias.

## 10. Métricas futuras

Preparar puntos para:

- requests total;
- latency;
- errors;
- provider latency;
- provider errors;
- cache hit ratio.

## 11. SLO inicial orientativo

Para una versión académica/pequeña:

- disponibilidad objetivo 99.5%;
- error rate interno <1% excluyendo fallas demostrables del proveedor;
- p95 backend cacheado <500 ms.

## 12. Resiliencia

Implementar:

- timeout;
- caché;
- retry limitado;
- manejo 429;
- fallback UI;
- circuit breaker solo si aporta valor real.

## 13. Privacidad

MVP:

- sin login;
- sin analytics invasivo;
- sin vender datos;
- geolocalización solo por consentimiento;
- no persistir coordenadas en backend;
- documentar si se integra telemetría futura.

## 14. Definition of Done de calidad

- [ ] `ruff check` pasa.
- [ ] formatter pasa.
- [ ] `mypy` pasa en módulos propios.
- [ ] pytest pasa.
- [ ] cobertura cumple.
- [ ] mutation suite base creada.
- [ ] no secrets.
- [ ] dependencias auditadas.
- [ ] logs estructurados.
- [ ] errores no filtran traceback al cliente.
