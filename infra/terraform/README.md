# Terraform Infrastructure for ProyectoClimatico

This directory contains Infrastructure as Code (IaC) to deploy **ProyectoClimatico** on AWS using Amazon ECS Fargate, Application Load Balancer (ALB), Amazon ECR, IAM, and CloudWatch.

## Structure

```text
infra/terraform/
├─ modules/
│  ├─ network/       # VPC, Subnets, Internet Gateway, Security Groups
│  ├─ ecr/           # ECR Container Repositories for backend & frontend
│  ├─ alb/           # Application Load Balancer & Target Groups
│  ├─ ecs/           # ECS Fargate Cluster, Task Definitions & Services
│  ├─ iam/           # Task Execution & OIDC Roles
│  └─ observability/ # CloudWatch Log Groups
└─ envs/
   ├─ dev/           # Development environment deployment
   └─ prod/          # Production environment deployment
```

## Validation Commands

```bash
# Format check
terraform fmt -check -recursive

# Initialize & Validate
cd envs/dev
terraform init -backend=false
terraform validate
```
