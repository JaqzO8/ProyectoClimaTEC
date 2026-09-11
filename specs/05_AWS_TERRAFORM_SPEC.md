# SPEC-05 — AWS + Terraform

**ID:** SPEC-05  
**Prioridad:** P0 para infraestructura  
**Objetivo:** desplegar ProyectoClimatico en AWS de forma reproducible.

## 1. Arquitectura objetivo

```text
Internet
   |
   v
Application Load Balancer
   |----------------------|
   | /api/*               | /*
   v                      v
ECS Fargate Backend    ECS Fargate Frontend
   |                      |
   +----------+-----------+
              |
              v
         Internet/API clima

Container images:
GitHub Actions -> Amazon ECR -> ECS
```

## 2. Servicios AWS

Obligatorios:

- Amazon ECR
  - `proyectoclimatico-backend`
  - `proyectoclimatico-frontend`
- Amazon ECS
- AWS Fargate
- Application Load Balancer
- VPC/subnets/security groups
- CloudWatch Logs
- IAM roles

Opcionales:

- Route 53;
- ACM;
- AWS WAF;
- CloudWatch alarms;
- AWS Budgets.

## 3. Routing ALB

Reglas:

```text
/api/* -> backend target group
/health backend puede exponerse bajo ruta específica si se decide
/* -> frontend target group
```

En Fargate usar target type `ip`.

## 4. Seguridad de red

### Perfil `cost_optimized` — default académico/dev

- ALB público;
- tasks Fargate en subnets públicas con public IP;
- SG de tasks solo acepta tráfico entrante desde SG del ALB;
- no exponer puertos de containers directamente al mundo;
- salida HTTPS permitida para APIs/ECR según necesidades.

Esto evita NAT Gateway por defecto.

### Perfil `hardened`

- ALB en subnets públicas;
- tasks en subnets privadas;
- NAT Gateway o endpoints VPC pertinentes;
- multi-AZ.

Debe estar documentado el impacto de costos.

## 5. HTTPS

Si existe dominio:

- Route 53 opcional;
- certificado ACM;
- listener 443;
- redirect 80 -> 443.

Si no hay dominio todavía:

- desplegar primero con DNS del ALB;
- no inventar dominio.

## 6. Terraform

Estructura:

```text
infra/terraform/
├─ modules/
│  ├─ network/
│  ├─ ecr/
│  ├─ alb/
│  ├─ ecs/
│  ├─ iam/
│  └─ observability/
└─ envs/
   ├─ dev/
   └─ prod/
```

## 7. Variables Terraform

Mínimo:

```hcl
project_name
environment
aws_region
backend_image_tag
frontend_image_tag
backend_cpu
backend_memory
frontend_cpu
frontend_memory
desired_count_backend
desired_count_frontend
allowed_cidrs
domain_name
enable_https
deployment_profile
```

## 8. Outputs

```hcl
alb_dns_name
backend_ecr_repository_url
frontend_ecr_repository_url
ecs_cluster_name
backend_service_name
frontend_service_name
```

## 9. Estado Terraform

Para proyecto personal inicial puede empezar localmente.

Para trabajo colaborativo/producción, documentar migración a backend remoto seguro, por ejemplo almacenamiento S3 con locking soportado por la versión/configuración elegida.

Nunca versionar:

- `.terraform/`
- `*.tfstate`
- `*.tfstate.*`
- archivos con secretos.

## 10. ECS task definitions

Cada servicio:

- imagen ECR;
- CPU/memory variables;
- port mapping;
- logging `awslogs`;
- healthcheck;
- execution role;
- task role separado si procede;
- variables no sensibles;
- secretos desde servicio AWS cuando se necesiten.

## 11. Escalado

MVP:

```text
desired_count = 1
```

Producción robusta:

```text
desired_count >= 2
```

Auto Scaling opcional basado en CPU/memoria.

## 12. Logging

CloudWatch log groups:

```text
/proyectoclimatico/dev/backend
/proyectoclimatico/dev/frontend
/proyectoclimatico/prod/backend
/proyectoclimatico/prod/frontend
```

Definir retención configurable.

## 13. Health checks

ALB backend:

```text
/health
```

Frontend:

- ruta HTTP simple estable.

Evitar healthchecks que dependan de Open-Meteo.

## 14. IAM

Aplicar mínimo privilegio.

Separar:

- ECS task execution role;
- runtime task role;
- CI/CD deploy role.

No usar `AdministratorAccess` como requisito permanente.

## 15. CI/CD AWS

GitHub Actions:

1. autenticación AWS mediante OIDC;
2. login ECR;
3. build imágenes;
4. tag por SHA;
5. push ECR;
6. actualizar task definition;
7. desplegar ECS;
8. esperar estabilidad;
9. smoke test.

No usar credenciales AWS de larga duración cuando OIDC esté disponible.

## 16. Comandos de validación

```bash
terraform fmt -check -recursive
terraform init
terraform validate
terraform plan
```

`apply` solo cuando la cuenta/región estén configuradas.

## 17. Criterios de aceptación

- [ ] Terraform crea recursos principales.
- [ ] ECR contiene ambas imágenes.
- [ ] ECS corre frontend/backend.
- [ ] ALB enruta correctamente.
- [ ] health checks saludables.
- [ ] logs visibles en CloudWatch.
- [ ] tareas no aceptan tráfico público directo.
- [ ] rollback/documentación disponible.
