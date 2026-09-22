resource "aws_security_group" "ephemeral_sg" {
  name        = "sg-${var.project_name}-${var.branch}-${var.github_run_id}"
  description = "Security group for ephemeral test instance in PruebaRama"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP web traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  dynamic "ingress" {
    for_each = var.runner_ip != "" ? [var.runner_ip] : []
    content {
      description = "SSH access restricted to runner"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["${ingress.value}/32"]
    }
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "sg-${var.project_name}-${var.branch}-${var.github_run_id}"
  }
}

resource "aws_key_pair" "ephemeral_key" {
  count      = var.ssh_public_key != "" ? 1 : 0
  key_name   = "prueba-Rama-Climatica-${var.github_run_id}"
  public_key = var.ssh_public_key

  tags = {
    Name = "prueba-Rama-Climatica-${var.github_run_id}"
  }
}
