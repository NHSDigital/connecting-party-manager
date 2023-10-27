output "metadata" {
  value = {
    lambda_invoke_arn   = module.lambda_function.lambda_function_invoke_arn
    authoriser_iam_role = aws_iam_role.assume_role.arn,
    authoriser_name     = var.lambda_name
  }
}
