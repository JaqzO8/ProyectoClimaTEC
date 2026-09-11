output "alb_dns_name" {
  value = module.alb.alb_dns_name
}

output "backend_ecr_repository_url" {
  value = module.ecr.backend_repository_url
}

output "frontend_ecr_repository_url" {
  value = module.ecr.frontend_repository_url
}

output "ecs_cluster_name" {
  value = module.ecs.ecs_cluster_name
}

output "backend_service_name" {
  value = module.ecs.backend_service_name
}

output "frontend_service_name" {
  value = module.ecs.frontend_service_name
}
