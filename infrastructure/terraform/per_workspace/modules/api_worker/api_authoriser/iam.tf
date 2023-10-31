resource "aws_iam_role" "assume_role" {
  name = "${var.lambda_name}-apig"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "apigateway.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })

}

resource "aws_iam_role_policy" "invoke_function" {
  name = "default"
  role = aws_iam_role.assume_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "lambda:InvokeFunction",
        Effect   = "Allow",
        Resource = module.lambda_function.lambda_function_arn
      }
    ]
  })
}

