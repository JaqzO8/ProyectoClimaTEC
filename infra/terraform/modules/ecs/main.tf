resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"
  tags = { Environment = var.environment }
}
locals {
  public_url = var.frontend_public_url != "" ? var.frontend_public_url : "http://${var.alb_dns_name}"
  components = {
    backend = {
      image         = var.backend_image
      cpu           = var.backend_cpu
      memory        = var.backend_memory
      port          = 8000
      log_group     = var.backend_log_group_name
      desired_count = var.desired_count_backend
      target_group  = var.backend_target_group_arn
      health_path   = "/health"
      environment = [
        { name = "APP_ENV", value = var.environment },
        { name = "CORS_ORIGINS", value = local.public_url },
        { name = "OPEN_METEO_API_MODE", value = var.weather_api_mode },
        { name = "RATE_LIMIT_ENABLED", value = "true" },
        { name = "TRUST_ALB_HEADERS", value = "true" },
        { name = "LOG_LEVEL", value = "INFO" }
      ]
    }
    frontend = {
      image         = var.frontend_image
      cpu           = var.frontend_cpu
      memory        = var.frontend_memory
      port          = 3000
      log_group     = var.frontend_log_group_name
      desired_count = var.desired_count_frontend
      target_group  = var.frontend_target_group_arn
      health_path   = "/ping"
      environment = [
        { name = "FRONTEND_PUBLIC_URL", value = local.public_url },
        { name = "REFLEX_API_URL", value = local.public_url },
        { name = "BACKEND_INTERNAL_URL", value = local.public_url }
      ]
    }
  }
}
resource "aws_ecs_task_definition" "app" {
  for_each                 = local.components
  family                   = "${var.project_name}-${var.environment}-${each.key}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = each.value.cpu
  memory                   = each.value.memory
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn
  container_definitions = jsonencode([{
    name         = each.key
    image        = each.value.image
    essential    = true
    user         = "1000:1000"
    portMappings = [{ containerPort = each.value.port, hostPort = each.value.port }]
    environment  = each.value.environment
    secrets = each.key == "backend" && var.weather_secret_arn != "" ? [{
      name = "OPEN_METEO_API_KEY", valueFrom = var.weather_secret_arn
    }] : []
    healthCheck = {
      command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:${each.value.port}${each.value.health_path}', timeout=3)\""]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = each.value.log_group
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = each.key
      }
    }
  }])
}
resource "aws_ecs_service" "app" {
  for_each                           = local.components
  name                               = "${var.project_name}-${var.environment}-${each.key}-svc"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.app[each.key].arn
  desired_count                      = each.value.desired_count
  launch_type                        = "FARGATE"
  health_check_grace_period_seconds  = 90
  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  network_configuration {
    subnets          = var.public_subnet_ids
    security_groups  = [var.ecs_tasks_security_group_id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = each.value.target_group
    container_name   = each.key
    container_port   = each.value.port
  }
  lifecycle {
    # GitHub Actions owns application revisions; Terraform owns infrastructure.
    ignore_changes = [task_definition]
  }
}
moved {
  from = aws_ecs_task_definition.backend
  to   = aws_ecs_task_definition.app["backend"]
}
moved {
  from = aws_ecs_task_definition.frontend
  to   = aws_ecs_task_definition.app["frontend"]
}
moved {
  from = aws_ecs_service.backend
  to   = aws_ecs_service.app["backend"]
}
moved {
  from = aws_ecs_service.frontend
  to   = aws_ecs_service.app["frontend"]
}
