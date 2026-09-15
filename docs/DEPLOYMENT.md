# Desplegar en AWS

## Datos reales necesarios

En GitHub → Settings → Environments, crea `production` (o `development`)
y limita las ramas de despliegue a `main`. Agrega estas **variables**, sin valores secretos:

| Variable | Valor |
| --- | --- |
| AWS_REGION | Región real de los recursos |
| AWS_ROLE_ARN | ARN del rol con confianza OIDC para este repositorio y environment |
| ECS_CLUSTER | Nombre del clúster |
| ECS_BACKEND_SERVICE | Nombre del servicio FastAPI |
| ECS_FRONTEND_SERVICE | Nombre del servicio Reflex |
| ECR_BACKEND_REPOSITORY | Nombre del repositorio ECR del backend |
| ECR_FRONTEND_REPOSITORY | Nombre del repositorio ECR del frontend |
| FRONTEND_PUBLIC_URL | URL pública, HTTPS para producción |
| OPEN_METEO_API_MODE | commercial para la suscripción |
| OPEN_METEO_SECRET_ARN | ARN de Secrets Manager que contiene la clave |

También puedes configurar cada variable con `gh variable set NOMBRE --env production`,
que solicita el valor por entrada estándar. No pongas una API key en estas variables.

No se necesitan claves AWS permanentes en GitHub. OIDC usa credenciales temporales.
El rol de despliegue no puede leer la clave del clima; únicamente el rol de
ejecución ECS puede recuperar el secreto indicado.

## Guardar la API key

En AWS Secrets Manager crea un secreto de tipo “Other type of secret” y usa la
pestaña de texto plano para guardar **solo la clave de Open-Meteo**, sin JSON,
comillas ni salto de línea. Copia su ARN; no copies el valor a Terraform.

Configura `weather_secret_arn` en tu `terraform.tfvars` local. Si usas una clave
KMS propia, configura también `weather_kms_key_arn`. Terraform administra la
referencia y el permiso, no el valor secreto. Para un secreto JSON existente,
crea un secreto de texto plano compatible o adapta explícitamente la selección
de clave JSON en la definición ECS.

## Infraestructura existente

Revisa `terraform plan` con tus recursos importados y su estado real antes de
aplicar. El proyecto conserva las direcciones de recursos ECS anteriores mediante
bloques `moved`. No ejecutes un segundo estado sobre infraestructura ya existente.
No se ha realizado ningún `apply` desde este entorno sin cuenta y región verificadas.

## Primera instalación

1. Usa Terraform 1.14+ y un perfil AWS autenticado, preferiblemente AWS IAM Identity Center.
2. Registra el proveedor IAM OIDC `https://token.actions.githubusercontent.com`
   con audiencia `sts.amazonaws.com` si aún no existe en tu cuenta.
3. Copia `infra/terraform/envs/prod/terraform.tfvars.example` a `terraform.tfvars`
   en ese directorio y completa los campos vacíos. Los archivos `*.tfvars` están ignorados.
4. Crea o usa un bucket S3 privado con cifrado, versionado y bloqueo de acceso público.
   El backend de producción usa locking nativo S3. No envíes estados como artifacts.
5. Usa un dominio real con certificado ACM emitido en la misma región del ALB.
   Configura `frontend_public_url` y `certificate_arn`; el DNS debe apuntar al ALB.
6. Inicializa y revisa el plan:

```bash
terraform -chdir=infra/terraform/envs/prod init -backend-config="bucket=BUCKET_REAL" -backend-config="key=proyectoclimatico/prod/terraform.tfstate" -backend-config="region=REGION_REAL"
terraform -chdir=infra/terraform/envs/prod plan
terraform -chdir=infra/terraform/envs/prod apply
```

La plantilla inicial deja ambos servicios con `desired_count=0` para crear ECR
y las task definitions antes de disponer de imágenes. Los tags `bootstrap`
identifican este arranque; no son imágenes meteorológicas simuladas.

7. Configura las variables GitHub con los outputs de Terraform. Los nombres ECR
   se obtienen de las URLs exportadas. Establece `desired_count_backend=2` y
   `desired_count_frontend=2` para producción y aplica ese cambio. Durante el
   primer despliegue las tareas iniciales todavía no podrán arrancar hasta que
   Actions publique el primer SHA y actualice las definiciones.
8. Ejecuta **Deploy to AWS ECS** desde `main` sobre `production`, después de
   tener CI aprobado para ese commit. Observa la estabilidad y los smoke tests.

El perfil implementado es `cost_optimized`: ALB público y Fargate con IP pública,
con entrada únicamente desde el security group del ALB. No incluye NAT Gateway.
La variante de subnets privadas/endpoints VPC requiere una ampliación de red.
AWS factura estos recursos según su uso; Terraform no supone que sean gratuitos.

## Validación sin credenciales

```bash
terraform fmt -check -recursive infra/terraform
terraform -chdir=infra/terraform/envs/dev init -backend=false -lockfile=readonly
terraform -chdir=infra/terraform/envs/dev validate
terraform -chdir=infra/terraform/envs/prod init -backend=false -lockfile=readonly
terraform -chdir=infra/terraform/envs/prod validate
```

`validate` verifica la configuración, pero no comprueba permisos, cuotas, cuenta,
dominio o existencia del secreto. Eso requiere `plan` y un despliegue real.

## Seguridad y operación

- La confianza IAM se limita a `repo:JaqzO8/ProyectoClimaTEC:environment:production`
  cuando esos valores se proporcionan a Terraform. Restringe ese environment a `main`.
- Los permisos abarcan solamente los repositorios ECR, servicios ECS y roles de
  tareas de este proyecto. Algunas APIs de registro/descripción de ECS y login
  ECR necesitan `Resource: "*"`; no se usa AdministratorAccess.
- Terraform mantiene la infraestructura. GitHub Actions mantiene la revisión de
  task definition de cada servicio; `ignore_changes` evita revertirla en un apply.
- Las imágenes usan SHA inmutable y lockfiles con hashes. La URL pública del
  frontend se fija al compilar: cambiarla requiere un nuevo commit y build.
- Reflex usa un proceso por tarea y afinidad de sesión en el ALB. El estado no
  persiste en disco; las preferencias permanecen en el navegador.
- Los logs en CloudWatch tienen la retención configurada por el módulo.
- Tras rotar la API key en Secrets Manager, despliega nuevas tareas para recargarla.

## Rollback

Actions registra las revisiones anteriores antes de actualizar servicios.
Si falla el update, la estabilidad o los smoke tests, restaura ambas revisiones
y deja el workflow en estado fallido. El circuit breaker de ECS también está habilitado.
La validación final comprueba que la revisión deseada coincide; una reversión
automática de ECS no se confunde con un despliegue exitoso.

Para rollback manual, identifica la revisión anterior del servicio y ejecuta:

```bash
aws ecs update-service --cluster CLUSTER_REAL --service SERVICIO_REAL --task-definition REVISION_ANTERIOR
aws ecs wait services-stable --cluster CLUSTER_REAL --services SERVICIO_REAL
```

Los identificadores en mayúsculas de este documento son instrucciones para
rellenar con valores reales; el workflow no contiene ARN o cuentas ficticias.
