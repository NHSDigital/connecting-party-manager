output "lambda_arn" {
  value = module.lambda_function.lambda_function_arn
}

output "lambda_role_arn" {
  value = module.lambda_function.lambda_role_arn
}

output "lambda_role_name" {
  value = module.lambda_function.lambda_role_name
}

output "metadata" {
  value = {
    lambda_invoke_arn   = module.lambda_function.lambda_function_invoke_arn
    authoriser_iam_role = module.lambda_function.lambda_role_arn
    authoriser_name     = var.lambda_name
  }
}
