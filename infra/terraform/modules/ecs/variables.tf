variable "project_name" {
  type    = string
  default = "proyectoclimatico"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "backend_image" {
  type = string
}

variable "frontend_image" {
  type = string
}

variable "backend_cpu" {
  type    = string
  default = "256"
}

variable "backend_memory" {
  type    = string
  default = "512"
}

variable "frontend_cpu" {
  type    = string
  default = "256"
}

variable "frontend_memory" {
  type    = string
  default = "512"
}

variable "desired_count_backend" {
  type    = number
  default = 1
}

variable "desired_count_frontend" {
  type    = number
  default = 1
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "ecs_tasks_security_group_id" {
  type = string
}

variable "backend_target_group_arn" {
  type = string
}

variable "frontend_target_group_arn" {
  type = string
}

variable "ecs_execution_role_arn" {
  type = string
}

variable "ecs_task_role_arn" {
  type = string
}

variable "backend_log_group_name" {
  type = string
}

variable "frontend_log_group_name" {
  type = string
}

variable "alb_dns_name" {
  type = string
}

variable "frontend_public_url" { type = string }
variable "weather_api_mode" { type = string }
variable "weather_secret_arn" { type = string }
