resource "aws_cloudwatch_log_group" "ecs_task_log_group" {
  name              = "/ecs/${var.project_name}-task-logs"
  retention_in_days = 7
}



