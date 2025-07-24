resource "aws_sfn_state_machine" "spike_polars_step_function" {
  name     = "${var.project_name}-ecs-task-runner-sfn"
  role_arn = aws_iam_role.sfn_execution_role.arn

  definition = jsonencode({
    Comment = "Runs a simple ECS Fargate task and waits for it to complete."
    StartAt = "RunSpikePolarsECS"
    States = {
      RunSpikePolarsECS = {
        Type     = "Task"
        Resource = "arn:aws:states:::ecs:runTask.sync" # .sync waits for task completion
        Parameters = {
          Cluster        = aws_ecs_cluster.spike_polars_cluster.arn,
          TaskDefinition = aws_ecs_task_definition.spike_polars_task_definition.arn,
          LaunchType     = "FARGATE",
          NetworkConfiguration = {
            AwsvpcConfiguration = {
              Subnets        = data.aws_subnets.public.ids,
              SecurityGroups = [aws_security_group.ecs_task_sg.id],
              AssignPublicIp = "ENABLED"
            }
          }
        }
        End = true
      }
    }
  })
}