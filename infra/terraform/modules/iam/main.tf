data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}

locals {
  account_prefix = "arn:${data.aws_partition.current.partition}"
  service_prefix = "${var.project_name}-${var.environment}"
  ecs_trust = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}
resource "aws_iam_role" "ecs_execution" {
  name               = "${local.service_prefix}-ecs-execution-role"
  assume_role_policy = local.ecs_trust
}
resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "${local.account_prefix}:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_iam_role_policy" "weather_secret" {
  count = var.weather_secret_arn != "" ? 1 : 0
  name  = "read-weather-key"
  role  = aws_iam_role.ecs_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat([{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [var.weather_secret_arn]
      }], var.weather_kms_key_arn != "" ? [{
      Effect   = "Allow"
      Action   = ["kms:Decrypt"]
      Resource = [var.weather_kms_key_arn]
    }] : [])
  })
}
resource "aws_iam_role" "ecs_task" {
  name               = "${local.service_prefix}-ecs-task-role"
  assume_role_policy = local.ecs_trust
}
resource "aws_iam_role" "github_oidc" {
  name = "${local.service_prefix}-github-oidc-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = var.github_oidc_provider_arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:environment:${var.github_environment}"
        }
      }
    }]
  })
}
resource "aws_iam_role_policy" "github_deploy" {
  name = "deploy-climate-services"
  role = aws_iam_role.github_oidc.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken", "ecs:RegisterTaskDefinition", "ecs:DescribeTaskDefinition"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["ecr:BatchCheckLayerAvailability", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage", "ecr:DescribeImages"]
        Resource = var.ecr_repository_arns
      },
      {
        Effect = "Allow"
        Action = ["ecs:DescribeServices", "ecs:UpdateService"]
        Resource = [
          "${local.account_prefix}:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:service/${local.service_prefix}-cluster/${local.service_prefix}-backend-svc",
          "${local.account_prefix}:ecs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:service/${local.service_prefix}-cluster/${local.service_prefix}-frontend-svc"
        ]
      },
      {
        Effect    = "Allow"
        Action    = ["iam:PassRole"]
        Resource  = [aws_iam_role.ecs_execution.arn, aws_iam_role.ecs_task.arn]
        Condition = { StringEquals = { "iam:PassedToService" = "ecs-tasks.amazonaws.com" } }
      }
    ]
  })
}
