output "api_gateway_id" {
  value = aws_api_gateway_rest_api.api_gateway_rest_api.id
}

output "execution_arn" {
  value = aws_api_gateway_rest_api.api_gateway_rest_api.execution_arn
}

output "kms_key" {
  value = module.kms.key_id
}

output "invoke_url" {
  value = aws_api_gateway_stage.api_gateway_stage.invoke_url
}

output "api_base_url" {
  value = "https://${var.domain}"
}
