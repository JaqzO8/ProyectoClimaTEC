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

variable "aws_account_id" {
  type    = string
  default = "123456789012"
}

variable "backend_image" {
  type    = string
  default = ""
}

variable "frontend_image" {
  type    = string
  default = ""
}
