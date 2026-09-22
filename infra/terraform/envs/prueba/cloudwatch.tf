# CloudWatch configuration & metrics namespace definition for ephemeral environment

locals {
  cw_namespace = "${var.project_name}/${var.branch}"
}

resource "aws_cloudwatch_metric_alarm" "high_cpu_alarm" {
  alarm_name          = "alarm-${var.project_name}-${var.branch}-${var.github_run_id}-cpu"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 90
  alarm_description   = "Ephemeral instance high CPU utilization"

  dimensions = {
    InstanceId = aws_instance.ephemeral_server.id
  }

  tags = {
    Name = "alarm-${var.project_name}-${var.branch}-${var.github_run_id}-cpu"
  }
}
