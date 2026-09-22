resource "aws_iam_role" "ephemeral_ec2_role" {
  name = "role-${var.project_name}-${var.branch}-${var.github_run_id}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "role-${var.project_name}-${var.branch}-${var.github_run_id}"
  }
}

resource "aws_iam_role_policy_attachment" "cw_agent_policy" {
  role       = aws_iam_role.ephemeral_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_instance_profile" "ephemeral_instance_profile" {
  name = "profile-${var.project_name}-${var.branch}-${var.github_run_id}"
  role = aws_iam_role.ephemeral_ec2_role.name

  tags = {
    Name = "profile-${var.project_name}-${var.branch}-${var.github_run_id}"
  }
}
