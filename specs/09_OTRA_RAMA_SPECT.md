# SPEC – Automatización CI/CD de `PruebaRama`

## 1. Objetivo

Implementar un proceso CI/CD completamente automatizado para el proyecto climático.

Debe existir una rama denominada:

`PruebaRama`

Esta rama será utilizada como entorno alternativo de integración, pruebas y validación antes de permitir la incorporación de cambios a `main`.

El sistema deberá automatizar:

1. Validación local.
2. Ejecución de pruebas.
3. Medición de cobertura.
4. Rechazo de cambios con cobertura inferior al 80 %.
5. Push hacia GitHub.
6. Ejecución automática de GitHub Actions.
7. Validación nuevamente dentro de CI.
8. Creación automática de infraestructura AWS con Terraform.
9. Despliegue del sistema.
10. Pruebas sobre la instancia real.
11. Monitoreo mediante CloudWatch.
12. Recolección de resultados.
13. Destrucción automática de todos los recursos temporales.
14. Habilitación de la fusión con `main` solamente cuando las validaciones sean satisfactorias.

---

# 2. Arquitectura del flujo

El proceso deberá seguir obligatoriamente esta secuencia:

```text
DESARROLLADOR / CODEX
        │
        ▼
Ejecutar SPEC
        │
        ▼
Pruebas locales
        │
        ├── Falla ──────────► DETENER
        │
        ▼
Coverage >= 80 %
        │
        ├── No ─────────────► DETENER
        │
        ▼
Lint / validaciones
        │
        ├── Falla ──────────► DETENER
        │
        ▼
Commit
        │
        ▼
Push → PruebaRama
        │
        ▼
GitHub Actions
        │
        ▼
CI
├── Tests
├── Coverage >= 80 %
├── Lint
├── Docker Build
├── Terraform fmt
└── Terraform validate
        │
        ▼
Autenticación GitHub → AWS mediante OIDC
        │
        ▼
Terraform Apply
        │
        ▼
AWS
├── Security Group
├── Key Pair temporal
├── IAM Role
├── Instance Profile
└── EC2 Ubuntu 24.04
        │
        ▼
Configurar servidor
        │
        ▼
Deploy aplicación
        │
        ▼
Pruebas HTTP / integración
        │
        ▼
CloudWatch
├── CPU
├── Memoria
├── Disco
└── Red
        │
        ▼
Guardar resultados
        │
        ▼
Terraform Destroy
        │
        ▼
Eliminar recursos temporales
```

---

# 3. Política de ramas

Se utilizarán principalmente:

```text
main
PruebaRama
```

## `PruebaRama`

Será la rama de:

* desarrollo controlado;
* experimentación;
* validación;
* pruebas;
* despliegue temporal;
* pruebas AWS;
* integración antes de producción.

Todo cambio deberá pasar primero por `PruebaRama`.

## `main`

Representará código estable.

No deberán realizarse modificaciones automáticas directamente sobre `main` sin haber pasado previamente por los controles definidos.

El flujo esperado será:

```text
feature/cambio
      │
      ▼
PruebaRama
      │
      ▼
CI exitoso
      │
      ▼
Pull Request
      │
      ▼
main
```

La rama `main` deberá configurarse como rama protegida.

La fusión solamente deberá permitirse cuando los checks requeridos hayan terminado satisfactoriamente.

---

# 4. Quality Gate

Se establece:

```text
COVERAGE_MINIMUM = 80
```

El 80 % se interpretará como cobertura mínima automática de código mediante pruebas.

Para proyectos Python deberá utilizarse preferentemente:

```bash
pytest
pytest-cov
```

Ejemplo conceptual:

```bash
pytest \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-fail-under=80
```

Si la estructura del proyecto no utiliza `src`, Codex deberá identificar automáticamente el paquete principal y modificar el parámetro `--cov`.

### Condición

```text
coverage < 80 %
        ↓
FAIL
```

```text
coverage >= 80 %
        ↓
PASS
```

No se permitirá deployment AWS cuando:

* falle una prueba;
* coverage sea menor de 80 %;
* falle el lint;
* falle el build;
* Terraform no sea válido.

---

# 5. Validaciones obligatorias

Antes del deployment deberán ejecutarse como mínimo:

```text
Unit Tests            PASS
Integration Tests     PASS
Coverage              >= 80 %
Lint                   PASS
Docker Build           PASS
Terraform fmt          PASS
Terraform validate     PASS
```

Opcionalmente podrán incorporarse:

```text
Security Scan
Dependency Scan
SAST
Mutation Testing
Gherkin / BDD
```

Pero estos controles no deberán romper innecesariamente el flujo inicial.

---

# 6. Push automático

La ejecución local del SPEC podrá preparar y publicar `PruebaRama`.

Proceso conceptual:

```bash
git fetch origin
git checkout PruebaRama
```

Si no existe:

```bash
git checkout -b PruebaRama
```

Ejecutar posteriormente todas las pruebas.

SOLAMENTE cuando las validaciones sean satisfactorias:

```bash
git add .
git commit -m "ci: validaciones aprobadas para PruebaRama"
git push -u origin PruebaRama
```

Codex NO deberá realizar `git push` cuando:

```text
Tests = FAIL
Coverage < 80 %
Build = FAIL
Lint = FAIL
```

Nunca deberá realizar:

```bash
git push --force
```

sobre `main`.

---

# 7. GitHub Actions

Crear:

```text
.github/
└── workflows/
    ├── pruebarama-ci.yml
    └── pruebarama-aws.yml
```

El workflow deberá reaccionar a:

```yaml
on:
  push:
    branches:
      - PruebaRama

  pull_request:
    branches:
      - main
```

---

# 8. Etapa CI

`pruebarama-ci.yml` deberá ejecutar:

```text
checkout
↓
setup Python
↓
instalar dependencias
↓
lint
↓
tests
↓
coverage
↓
build
↓
Terraform fmt
↓
Terraform validate
```

El job deberá llamarse de forma clara, por ejemplo:

```text
quality-gate
```

Este check posteriormente será marcado como obligatorio para fusionar hacia `main`.

---

# 9. Regla del 80 %

Debe existir una barrera real en CI.

No bastará con mostrar la cobertura.

El comando deberá devolver código de error cuando:

```text
coverage < 80
```

De esta forma:

```text
79.99 % → FAIL
80.00 % → PASS
85.00 % → PASS
100 %    → PASS
```

El deployment dependerá explícitamente del Quality Gate.

Ejemplo lógico:

```text
quality-gate
      │
      ▼
deploy-aws
```

Nunca:

```text
quality-gate FAIL
      │
      └──────► deploy
```

---

# 10. Infraestructura como código

Toda la infraestructura temporal deberá ser gestionada con:

```text
Terraform
```

Crear:

```text
infra/
└── terraform/
    ├── versions.tf
    ├── provider.tf
    ├── variables.tf
    ├── main.tf
    ├── networking.tf
    ├── security.tf
    ├── iam.tf
    ├── cloudwatch.tf
    ├── outputs.tf
    └── user-data.sh
```

No deberán crearse manualmente instancias EC2 para cada deployment.

---

# 11. Configuración AWS

Utilizar:

```text
Región:            us-east-1
Instancia:         t3.micro
Sistema operativo: Ubuntu Server 24.04 LTS
Arquitectura:      AMD64/x86_64
Volumen:           8 GB
Tipo volumen:      gp3
Puerto web:        TCP/80
Puerto SSH:        TCP/22
Monitoring EC2:    Basic
```

No deberá utilizarse un AMI ID fijo.

Terraform deberá localizar automáticamente la versión actual de Ubuntu 24.04 publicada oficialmente por Canonical.

Propietario oficial:

```text
099720109477
```

Filtro esperado:

```text
ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*
```

Weather API:
api_wrapper: OpenWeatherMapAPIWrapper = Field(default_factory=OpenWeatherMapAPIWrapper)

De esta forma no habrá dependencia de un AMI específico que pueda quedar obsoleto.

---

# 12. Identificación dinámica de recursos

Todos los recursos deberán utilizar nombres identificables y evitar colisiones.

Ejemplo:

```text
Project        = ProyectoClimatico
Environment    = prueba
Branch         = PruebaRama
GitHubRunId    = <run_id>
```

Nombre EC2:

```text
ProyectoClimatico-PruebaRama-<run_id>
```

Security Group:

```text
sg-ProyectoClimatico-PruebaRama-<run_id>
```

Key Pair:

```text
prueba-Rama-Climatica-<run_id>
```

De esta manera dos ejecuciones diferentes no deberán reutilizar accidentalmente los mismos recursos.

---

# 13. SSH

Para Ubuntu 24.04:

```text
SSH_USER=ubuntu
```

Nunca asumir:

```text
ec2-user
```

para las instancias Ubuntu.

La conexión deberá realizarse conceptualmente como:

```bash
ssh -i clave.pem ubuntu@DNS_PUBLICO
```

---

# 14. Key Pair temporal

No almacenar permanentemente una clave privada de EC2 dentro del repositorio.

Durante GitHub Actions:

1. Generar una clave SSH temporal.
2. Mantener la clave privada únicamente en GitHub Runner.
3. Entregar a Terraform únicamente la clave pública.
4. Terraform creará el AWS Key Pair.
5. Utilizar la clave privada temporal para el deployment.
6. Destruir el AWS Key Pair mediante `terraform destroy`.
7. GitHub Runner eliminará su entorno al finalizar.

Nunca deberá realizarse:

```text
git add *.pem
```

Agregar a `.gitignore`:

```text
*.pem
*.key
```

---

# 15. Security Group

Puerto HTTP:

```text
TCP 80
Source: 0.0.0.0/0
```

Puerto SSH:

```text
TCP 22
```

No abrir el SSH universalmente cuando pueda evitarse.

Preferentemente GitHub Actions deberá detectar su IP pública temporal:

```text
RUNNER_IP/32
```

y Terraform permitirá SSH solamente desde esa dirección.

Conceptualmente:

```text
22 → RUNNER_IP/32
80 → 0.0.0.0/0
```

---

# 16. Protección de metadatos

La instancia deberá utilizar IMDSv2.

Terraform deberá configurar:

```text
http_endpoint = enabled
http_tokens   = required
```

---

# 17. Docker

Si el ProyectoClimatico dispone de Docker, el servidor deberá:

```text
instalar Docker (DockerEngine)
↓
instalar Docker Compose Plugin (CLI)
↓
recibir aplicación web
↓
construir/descargar imagen
↓
ejecutar contenedor
```

El contenedor web deberá exponer su servicio al puerto configurado para HTTP.

Ejemplo:

```text
EC2:80
    ↓
Docker
    ↓
Aplicación climática
```

---

# 18. Prueba de disponibilidad

Después del deployment deberá ejecutarse automáticamente una prueba HTTP.

Ejemplo:

```bash
curl --fail http://PUBLIC_IP/
```

Si existe healthcheck:

```bash
curl --fail http://PUBLIC_IP/health
```

Resultado requerido:

```text
HTTP 200
```

Deberá implementarse retry porque la aplicación puede necesitar algunos segundos para inicializarse.

Ejemplo conceptual:

```text
Máximo: 10 intentos
Intervalo: 10 segundos
```

---

# 19. CloudWatch

La instancia será monitorizada utilizando Amazon CloudWatch.

## Métricas EC2 estándar

Utilizar:

```text
CPUUtilization
NetworkIn
NetworkOut
DiskReadBytes
DiskWriteBytes
StatusCheckFailed
```

Configuración:

```text
EC2 Detailed Monitoring = false
```

manteniendo el monitoreo básico.

---

# 20. CloudWatch Agent

Como EC2 no proporciona directamente uso de RAM ni porcentaje de disco del sistema operativo, deberá instalarse:

```text
Amazon CloudWatch Agent
```

La instancia deberá contar con un IAM Instance Profile con permisos únicamente suficientes para publicar las métricas necesarias.

Recopilar:

```text
mem_used_percent
disk_used_percent
```

Opcionalmente:

```text
diskio_reads
diskio_writes
```

Intervalo:

```text
metrics_collection_interval = 300
```

equivalente a cinco minutos.

Namespace recomendado:

```text
ProyectoClimatico/PruebaRama
```

---

# 21. Métricas finales

Durante las pruebas deberá recopilarse como mínimo:

```text
CPU %
RAM %
Disco %
NetworkIn
NetworkOut
HTTP status
Tiempo de respuesta
```

Las métricas deberán poder consultarse antes de destruir la infraestructura.

Cuando sea posible, exportar los resultados a un archivo como:

```text
artifacts/
├── coverage.xml
├── test-results.xml
├── deployment-summary.json
└── cloudwatch-metrics.json
```

Los archivos deberán publicarse como artifacts de GitHub Actions antes de ejecutar `terraform destroy`.

---

# 22. Ventana de validación

Debido a que el monitoreo requerido tiene intervalos de cinco minutos, no destruir inmediatamente la máquina después de arrancarla.

La automatización deberá mantener el ambiente activo durante una ventana suficiente para obtener al menos una muestra válida.

Durante esa ventana ejecutar:

```text
healthcheck
pruebas HTTP
pruebas de integración
pruebas de carga ligera
```

Posteriormente recuperar las métricas.

---

# 23. Destrucción

La infraestructura de `PruebaRama` es EFÍMERA.

Después de:

```text
Deploy
+
Tests AWS
+
Métricas
```

deberá ejecutarse:

```bash
terraform destroy -auto-approve
```

incluso si alguna prueba posterior al `terraform apply` falla.

El paso de cleanup deberá configurarse conceptualmente como:

```text
if: always()
```

para reducir el riesgo de dejar recursos ejecutándose.

---

# 24. No detener antes de destruir

No será obligatorio ejecutar:

```text
aws ec2 stop-instances
```

antes de:

```text
terraform destroy
```

porque Terraform puede terminar directamente la instancia.

Por lo tanto el flujo normal será:

```text
RUNNING
   ↓
pruebas
   ↓
métricas
   ↓
terraform destroy
   ↓
TERMINATED
```

La acción `stop` sólo deberá implementarse cuando exista alguna prueba específica que lo requiera.

---

# 25. Recursos eliminados

Al finalizar deberán eliminarse automáticamente todos los recursos efímeros creados por Terraform, incluyendo según corresponda:

```text
EC2
Security Group
Key Pair AWS
IAM Instance Profile temporal
CloudWatch Alarm temporal
CloudWatch Dashboard temporal
recursos auxiliares del entorno
```

No eliminar recursos compartidos o globales utilizados por otros proyectos.

---

# 26. Tags obligatorios

Todos los recursos deberán recibir tags:

```text
Project     = ProyectoClimatico
Environment = Test
Branch      = PruebaRama
ManagedBy   = Terraform
Ephemeral   = true
RunId       = <github.run_id>
```

Esto permitirá identificar fácilmente cualquier infraestructura que accidentalmente no haya sido destruida.

---

# 27. Autenticación GitHub → AWS

No utilizar credenciales AWS permanentes cuando OIDC esté disponible.

Utilizar:

```text
GitHub Actions
      ↓
GitHub OIDC
      ↓
AWS STS
      ↓
IAM Role
      ↓
Credenciales temporales
```

Workflow:

```yaml
permissions:
  contents: read
  id-token: write
```

Utilizar la acción oficial:

```text
aws-actions/configure-aws-credentials
```

y asumir un IAM Role creado específicamente para CI/CD.

---

# 28. Permisos IAM

Aplicar principio de mínimo privilegio.

El role de GitHub deberá disponer únicamente de los permisos necesarios para gestionar los recursos definidos en Terraform.

No utilizar:

```text
AdministratorAccess
```

como configuración definitiva.

El EC2 deberá tener un IAM Role separado del utilizado por GitHub Actions.

---

# 29. Bootstrap

Existe una excepción inicial.

Antes de que GitHub Actions pueda administrar AWS automáticamente deberá existir una relación de confianza:

```text
GitHub OIDC
        ↕
AWS IAM
```

Por ello se permitirá una configuración inicial denominada:

```text
bootstrap/
```

que cree:

```text
GitHub OIDC Provider
IAM Role de CI/CD
IAM Trust Policy
```

Esta preparación deberá realizarse una sola vez.

Después de ese bootstrap ninguna instancia EC2 deberá crearse manualmente.

---

# 30. Pull Request hacia main

Cuando `PruebaRama` haya superado las validaciones, deberá poder crearse:

```text
PruebaRama
      ↓
Pull Request
      ↓
main
```

La rama `main` deberá tener como mínimo:

```text
Require pull request
Require status checks
quality-gate obligatorio
bloqueo ante CI fallido
```

No realizar merge automático de código defectuoso.

---

# 31. Fallos

Si falla CI antes de crear AWS:

```text
FAIL
↓
No Terraform Apply
↓
No EC2
↓
No coste de infraestructura
```

Si falla después de crear AWS:

```text
FAIL
↓
Guardar logs
↓
Guardar artifacts
↓
Terraform Destroy
```

---

# 32. Resultado esperado

Ejecución satisfactoria:

```text
✓ Tests
✓ Coverage >= 80 %
✓ Lint
✓ Docker Build
✓ Terraform Validate
✓ AWS authentication
✓ EC2 creada
✓ Ubuntu 24.04
✓ Aplicación desplegada
✓ HTTP 200
✓ CloudWatch operativo
✓ Métricas obtenidas
✓ Artifacts guardados
✓ Recursos destruidos
```

Resultado final:

```text
DEPLOYMENT VALIDATION: PASSED
```

Si algún requisito obligatorio falla:

```text
DEPLOYMENT VALIDATION: FAILED
```

y no deberá aprobarse el merge hacia `main`.

---

# 33. Estructura final esperada

```text
ProyectoClimatico/
│
├── .github/
│   └── workflows/
│       ├── pruebarama-ci.yml
│       └── pruebarama-aws.yml
│
├── infra/
│   └── terraform/
│       ├── versions.tf
│       ├── provider.tf
│       ├── variables.tf
│       ├── main.tf
│       ├── networking.tf
│       ├── security.tf
│       ├── iam.tf
│       ├── cloudwatch.tf
│       ├── outputs.tf
│       └── user-data.sh
│
├── scripts/
│   ├── validate.sh
│   ├── validate.ps1
│   └── deploy-test.sh
│
├── tests/
│
├── src/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

Codex deberá adaptar esta estructura si el proyecto existente utiliza otros nombres de carpetas, pero no deberá eliminar o sobrescribir componentes funcionales existentes sin necesidad.

---

# 34. Criterio final de aceptación

La implementación estará terminada únicamente cuando pueda realizarse:

```text
modificar código
       ↓
ejecutar SPEC
       ↓
tests locales >= 80 %
       ↓
push PruebaRama
       ↓
GitHub Actions
       ↓
tests CI >= 80 %
       ↓
Terraform Apply
       ↓
crear AWS automáticamente
       ↓
deploy
       ↓
validar servidor
       ↓
CloudWatch
       ↓
guardar evidencia
       ↓
Terraform Destroy
       ↓
0 infraestructura temporal restante
```

sin necesidad de crear manualmente una nueva instancia EC2 desde la consola de AWS.
