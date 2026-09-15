variable "project_name" { type = string }
variable "environment" { type = string }
variable "github_repo" { type = string }
variable "github_environment" { type = string }
variable "github_oidc_provider_arn" { type = string }
variable "weather_secret_arn" {
  type    = string
  default = ""
}
variable "weather_kms_key_arn" {
  type    = string
  default = ""
}
variable "ecr_repository_arns" { type = list(string) }
variable "aws_region" { type = string }
