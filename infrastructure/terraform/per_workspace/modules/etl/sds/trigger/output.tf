output "lambda_function" {
  value = module.lambda_function
}

output "arn" {
  value = module.lambda_function.lambda_function_arn
}
