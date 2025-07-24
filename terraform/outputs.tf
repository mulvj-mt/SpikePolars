output "ecs_cluster_name" {
  description = "The name of the ECS cluster."
  value       = aws_ecs_cluster.spike_polars_cluster.id
}

output "ecs_task_definition_arn" {
  description = "The ARN of the ECS task definition."
  value       = aws_ecs_task_definition.spike_polars_task_definition.arn
}

output "step_function_arn" {
  description = "The ARN of the Step Functions State Machine."
  value       = aws_sfn_state_machine.spike_polars_step_function.id
}

output "step_function_console_url" {
  description = "Direct URL to the Step Function State Machine in the AWS Console."
  value       = "https://${var.aws_region}.console.aws.amazon.com/states/home?region=${var.aws_region}#/statemachines/view/${aws_sfn_state_machine.spike_polars_step_function.id}"
}