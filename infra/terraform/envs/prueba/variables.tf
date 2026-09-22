variable "aws_region" {
  description = "AWS Region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name tag"
  type        = string
  default     = "ProyectoClimatico"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "Test"
}

variable "branch" {
  description = "Branch name"
  type        = string
  default     = "PruebaRama"
}

variable "github_run_id" {
  description = "GitHub Actions Run ID for unique resource naming"
  type        = string
  default     = "local"
}

variable "runner_ip" {
  description = "Public IP of the GitHub Actions runner for SSH access"
  type        = string
  default     = ""
}

variable "ssh_public_key" {
  description = "Temporary SSH public key for EC2 instance access"
  type        = string
  default     = ""
}

variable "instance_type" {
  description = "EC2 Instance Type"
  type        = string
  default     = "t3.micro"
}

variable "volume_size" {
  description = "Root EBS Volume Size in GB"
  type        = number
  default     = 8
}
