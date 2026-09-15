terraform {
  required_version = ">= 1.14.0, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
provider "aws" { region = var.aws_region }

resource "terraform_data" "configuration" {
  lifecycle {
    precondition {
      condition     = var.weather_api_mode != "commercial" || var.weather_secret_arn != ""
      error_message = "Commercial Open-Meteo requires a real Secrets Manager ARN."
    }
    precondition {
      condition     = !var.enable_https || (var.certificate_arn != "" && startswith(var.frontend_public_url, "https://"))
      error_message = "HTTPS requires an ACM certificate and a real HTTPS public URL."
    }
    precondition {
      condition     = var.environment != "prod" || var.enable_https
      error_message = "Production requires HTTPS."
    }
  }
}
module "network" {
  source        = "../../modules/network"
  project_name  = var.project_name
  environment   = var.environment
  aws_region    = var.aws_region
  allowed_cidrs = var.allowed_cidrs
}
module "ecr" {
  source       = "../../modules/ecr"
  project_name = var.project_name
  environment  = var.environment
}
module "alb" {
  source                = "../../modules/alb"
  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.network.vpc_id
  public_subnet_ids     = module.network.public_subnet_ids
  alb_security_group_id = module.network.alb_security_group_id
  enable_https          = var.enable_https
  certificate_arn       = var.certificate_arn
}
module "iam" {
  source                   = "../../modules/iam"
  project_name             = var.project_name
  environment              = var.environment
  aws_region               = var.aws_region
  github_repo              = var.github_repo
  github_environment       = var.github_environment
  github_oidc_provider_arn = var.github_oidc_provider_arn
  weather_secret_arn       = var.weather_secret_arn
  weather_kms_key_arn      = var.weather_kms_key_arn
  ecr_repository_arns      = [module.ecr.backend_repository_arn, module.ecr.frontend_repository_arn]
}
module "observability" {
  source       = "../../modules/observability"
  project_name = var.project_name
  environment  = var.environment
}
module "ecs" {
  source                      = "../../modules/ecs"
  depends_on                  = [module.alb, module.iam, terraform_data.configuration]
  project_name                = var.project_name
  environment                 = var.environment
  aws_region                  = var.aws_region
  backend_image               = "${module.ecr.backend_repository_url}:${var.backend_image_tag}"
  frontend_image              = "${module.ecr.frontend_repository_url}:${var.frontend_image_tag}"
  backend_cpu                 = var.backend_cpu
  backend_memory              = var.backend_memory
  frontend_cpu                = var.frontend_cpu
  frontend_memory             = var.frontend_memory
  desired_count_backend       = var.desired_count_backend
  desired_count_frontend      = var.desired_count_frontend
  public_subnet_ids           = module.network.public_subnet_ids
  ecs_tasks_security_group_id = module.network.ecs_tasks_security_group_id
  backend_target_group_arn    = module.alb.backend_target_group_arn
  frontend_target_group_arn   = module.alb.frontend_target_group_arn
  ecs_execution_role_arn      = module.iam.ecs_execution_role_arn
  ecs_task_role_arn           = module.iam.ecs_task_role_arn
  backend_log_group_name      = module.observability.backend_log_group_name
  frontend_log_group_name     = module.observability.frontend_log_group_name
  alb_dns_name                = module.alb.alb_dns_name
  frontend_public_url         = var.frontend_public_url
  weather_api_mode            = var.weather_api_mode
  weather_secret_arn          = var.weather_secret_arn
}
