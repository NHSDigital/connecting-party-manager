output "api_gateway_id" {
  value = aws_apigatewayv2_api.api_gateway_v2.id
}

output "execution_arn" {
  value = aws_apigatewayv2_api.api_gateway_v2.execution_arn
}
