output "ecs_cluster_name" { value = aws_ecs_cluster.main.name }
output "backend_service_name" { value = aws_ecs_service.app["backend"].name }
output "frontend_service_name" { value = aws_ecs_service.app["frontend"].name }
