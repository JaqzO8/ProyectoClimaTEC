variable "project_name" {
  type    = string
  default = "proyectoclimatico"
}
variable "environment" {
  type    = string
  default = "dev"
}
variable "aws_region" { type = string }
variable "github_repo" { type = string }
variable "github_environment" { type = string }
variable "github_oidc_provider_arn" { type = string }
variable "backend_image_tag" {
  type    = string
  default = "bootstrap"
}
variable "frontend_image_tag" {
  type    = string
  default = "bootstrap"
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
  default = "512"
}
variable "frontend_memory" {
  type    = string
  default = "1024"
}
variable "desired_count_backend" {
  type    = number
  default = 1
}
variable "desired_count_frontend" {
  type    = number
  default = 1
}
variable "frontend_public_url" {
  type    = string
  default = ""
}
variable "enable_https" {
  type    = bool
  default = false
}
variable "certificate_arn" {
  type    = string
  default = ""
}
variable "weather_api_mode" {
  type    = string
  default = "free"
  validation {
    condition     = contains(["free", "commercial"], var.weather_api_mode)
    error_message = "Use free or commercial."
  }
}
variable "weather_secret_arn" {
  type    = string
  default = ""
}
variable "weather_kms_key_arn" {
  type    = string
  default = ""
}
variable "allowed_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}
