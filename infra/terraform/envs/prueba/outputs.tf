output "instance_id" {
  description = "ID of the created ephemeral EC2 instance"
  value       = aws_instance.ephemeral_server.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.ephemeral_server.public_ip
}

output "public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.ephemeral_server.public_dns
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.ephemeral_sg.id
}

output "cloudwatch_namespace" {
  description = "CloudWatch namespace for metrics"
  value       = local.cw_namespace
}
