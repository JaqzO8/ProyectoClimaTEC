# ProyectoClimatico — paquete de especificaciones SDD

Este paquete define cómo construir **ProyectoClimatico**, una aplicación web climática global, responsive y desplegable en AWS, desarrollada con enfoque **Spec-Driven Development (SDD)**.

## Objetivo del producto

Crear una plataforma web que permita:

- consultar condiciones meteorológicas actuales;
- localizar lugares de cualquier país;
- representar ciudad, provincia/departamento/estado/región y niveles administrativos equivalentes;
- usar geolocalización del navegador para mostrar el clima local;
- consultar pronóstico horario y diario;
- presentar una interfaz moderna de base blanca, accesible y responsive;
- ejecutarse localmente con Docker;
- desplegarse en AWS;
- mantenerse en un repositorio Git llamado `ProyectoClimatico`;
- ser construida de forma reproducible por Codex siguiendo especificaciones verificables.

## Arquitectura elegida

- **Lenguaje principal:** Python 3.13+
- **Backend:** FastAPI + Pydantic + HTTPX
- **Frontend:** Reflex (UI reactiva escrita principalmente en Python)
- **Proveedor meteorológico inicial:** Open-Meteo mediante una capa `WeatherProvider`
- **Contenedores:** Docker + Docker Compose
- **IaC:** Terraform
- **AWS:** ECR + ECS Fargate + Application Load Balancer + CloudWatch
- **CI/CD:** GitHub Actions + AWS OIDC
- **Calidad:** Ruff, mypy, pytest, pytest-asyncio, coverage, Hypothesis y mutation testing
- **API:** REST JSON versionada `/api/v1`
- **Arquitectura de código:** Clean Architecture pragmática / Hexagonal ligera

## Orden obligatorio de lectura para Codex

1. `specs/00_MASTER_SPEC.md`
2. `specs/01_BACKEND_SPEC.md`
3. `specs/02_FRONTEND_SPEC.md`
4. `specs/03_WEATHER_DATA_SPEC.md`
5. `specs/04_DOCKER_LOCAL_SPEC.md`
6. `specs/05_AWS_TERRAFORM_SPEC.md`
7. `specs/06_GIT_CICD_SPEC.md`
8. `specs/07_QUALITY_SECURITY_SPEC.md`
9. `specs/08_ACCEPTANCE_GHERKIN.md`
10. `CODEX_MASTER_PROMPT.md`

## Alcance MVP

El MVP no requiere cuentas de usuario, pagos ni base de datos. Debe ser **stateless** y consumir un proveedor climático externo a través del backend. La arquitectura debe dejar puntos de extensión para favoritos, alertas, historial, autenticación y proveedores meteorológicos alternativos.

## Regla de interpretación geográfica

No todos los países usan los términos “departamento” y “provincia”. El software normalizará los niveles administrativos externos como:

- `country`
- `admin1`
- `admin2`
- `admin3`
- `admin4`

La UI mostrará la denominación real devuelta por el proveedor cuando esté disponible.

## Fuentes técnicas de referencia

- Open-Meteo Forecast API: https://open-meteo.com/en/docs
- Open-Meteo Geocoding API: https://open-meteo.com/en/docs/geocoding-api
- FastAPI Docker: https://fastapi.tiangolo.com/deployment/docker/
- Reflex self-hosting: https://reflex.dev/docs/hosting/self-hosting
- AWS ECS/Fargate: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html
- AWS ECR + ECS: https://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_on_ECS.html
- GitHub Actions + AWS OIDC: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws


EC2 => Servidores virtuales en la nube
Dentro de la capa gratuita se obtiene varios servicios en las cuales se podrán utilizar de manera independiente para cada proyecto creado, distintos beneficios de obtimización y también adaptado a lo que se necesite , esto ayuda al rápido despliegue de servicios y aplicaciones   

Dependiendo del proyecto que se va a armar, nos dan instancias a escoger, por ejemplo:
t3.micro: Es una instancia de propósito general, ideal para cargas de trabajo de uso general con requisitos de cómputo y memoria equilibrados. Tarda 5-10 minutos en iniciarse.
t2.micro: Similar a la t3.micro pero con un rendimiento un poco menor. Tarda 5-10 minutos en iniciarse.
t3.small: Es una instancia de propósito general, ideal para cargas de trabajo de uso general con requisitos de cómputo y memoria equilibrados. Tarda 5-10 minutos en iniciarse.

Tenemos también servicios de seguridad como ssh, scp, sftp, etc.

Para conectarnos a un cliente ssh en Amazon se siguen los siguientes pasos:

Busque o descarge su archivo dde clave privada, asegura permisos con chmod.

CONSTRUCCION:

Como reconocer un tipp de aplicación, App de software u criterio de clasificación
Cuando salimos a desarrollar, los gráficos son clave, para ello los diseños de procesos nos permiten tener una versión as is, to be.
Recordemos que el ciclo de vida del software empieza con el Analisis de los requisitos, requerimientos funcionales del usuario, las famosas Historias de Usuario. 
Luego el Diseño de la arquitectura del software, el frontend y el backend.
Luego la Codificación, aqui es donde se ejecuta los primeros codigos, las primeras líneas de comando.
Luego la Validación y pruebas.
Luego la implementación
Luego el Mantenimiento y actualización de los módulos del software.

