terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "network" {
  source       = "../../modules/network"
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region
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
}

module "iam" {
  source         = "../../modules/iam"
  project_name   = var.project_name
  environment    = var.environment
  aws_account_id = var.aws_account_id
}

module "observability" {
  source       = "../../modules/observability"
  project_name = var.project_name
  environment  = var.environment
}

module "ecs" {
  source                       = "../../modules/ecs"
  project_name                 = var.project_name
  environment                  = var.environment
  aws_region                   = var.aws_region
  backend_image                = var.backend_image != "" ? var.backend_image : "${module.ecr.backend_repository_url}:latest"
  frontend_image               = var.frontend_image != "" ? var.frontend_image : "${module.ecr.frontend_repository_url}:latest"
  public_subnet_ids            = module.network.public_subnet_ids
  ecs_tasks_security_group_id = module.network.ecs_tasks_security_group_id
  backend_target_group_arn     = module.alb.backend_target_group_arn
  frontend_target_group_arn    = module.alb.frontend_target_group_arn
  ecs_execution_role_arn       = module.iam.ecs_execution_role_arn
  ecs_task_role_arn            = module.iam.ecs_task_role_arn
  backend_log_group_name       = module.observability.backend_log_group_name
  frontend_log_group_name      = module.observability.frontend_log_group_name
  alb_dns_name                 = module.alb.alb_dns_name
}
