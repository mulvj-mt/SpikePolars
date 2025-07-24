resource "aws_iam_role" "ecs_task_execution_role" {
  name_prefix = "${var.project_name}-ecs-exec-role-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name_prefix = "${var.project_name}-ecs-role-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_role_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role" "sfn_execution_role" {
  name_prefix = "${var.project_name}-sfn-exec-role-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "states.${var.aws_region}.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "sfn_ecs_policy" {
  name_prefix = "${var.project_name}-sfn-ecs-policy-"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecs:RunTask"
        ],
        Resource = [
          aws_ecs_task_definition.spike_polars_task_definition.arn,
          aws_ecs_cluster.spike_polars_cluster.arn
        ]
      },
      {
        Effect = "Allow",
        Action = "iam:PassRole",
        Resource = [
          aws_iam_role.ecs_task_execution_role.arn,
          aws_iam_role.ecs_task_role.arn
        ],
        Condition = {
          StringLike = {
            "iam:PassedToService" = [
              "ecs-tasks.amazonaws.com",
              "events.amazonaws.com"
            ]
          }
        }
      },
      {
        Effect = "Allow",
        Action = [
          "events:PutTargets",
          "events:PutRule",
          "events:DescribeRule"
        ],
        Resource = [
          "arn:aws:events:${var.aws_region}:${local.account_id}:rule/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "states:StartExecution",
          "states:StopExecution",
          "states:DescribeExecution",
          "states:ListExecutions"
        ],
        Resource = [
          "*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:${var.aws_region}:${local.account_id}:log-group:/aws/stepfunctions/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sfn_ecs_policy_attachment" {
  role       = aws_iam_role.sfn_execution_role.name
  policy_arn = aws_iam_policy.sfn_ecs_policy.arn
}

