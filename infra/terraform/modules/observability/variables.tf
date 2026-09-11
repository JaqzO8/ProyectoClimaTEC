variable "project_name" {
  type    = string
  default = "proyectoclimatico"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "retention_in_days" {
  type    = number
  default = 14
}
