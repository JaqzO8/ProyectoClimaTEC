provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Branch      = var.branch
      ManagedBy   = "Terraform"
      Ephemeral   = "true"
      RunId       = var.github_run_id
    }
  }
}
