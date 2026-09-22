data "aws_ami" "ubuntu_24_04" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

resource "aws_instance" "ephemeral_server" {
  ami                         = data.aws_ami.ubuntu_24_04.id
  instance_type               = var.instance_type
  key_name                    = var.ssh_public_key != "" ? aws_key_pair.ephemeral_key[0].key_name : null
  vpc_security_group_ids      = [aws_security_group.ephemeral_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.ephemeral_instance_profile.name
  associate_public_ip_address = true
  user_data                   = file("${path.module}/user-data.sh")

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required" # Enforce IMDSv2
  }

  root_block_device {
    volume_size           = var.volume_size
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }

  monitoring = false # Basic monitoring

  tags = {
    Name = "${var.project_name}-${var.branch}-${var.github_run_id}"
  }
}
