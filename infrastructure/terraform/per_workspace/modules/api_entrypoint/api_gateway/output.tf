output "api_gateway_id" {
  value = aws_api_gateway_rest_api.api_gateway_rest_api.id
}

output "execution_arn" {
  value = aws_api_gateway_rest_api.api_gateway_rest_api.execution_arn
}

output "kms_key" {
  value = module.kms.key_id
}
