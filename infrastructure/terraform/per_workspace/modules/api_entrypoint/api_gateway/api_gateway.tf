resource "aws_api_gateway_rest_api" "api_gateway_rest_api" {
  name        = var.name
  description = "API Gateway Rest API - autogenerated from swagger"
  # UNCOMMENT THIS WHEN ENABLING CUSTOM DOMAINS
  # disable_execute_api_endpoint = true
  body = sensitive(local.swagger_file)

  depends_on = [
    aws_cloudwatch_log_group.api_gateway_access_logs
  ]

}

resource "aws_api_gateway_deployment" "api_gateway_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id

  triggers = {
    redeployment    = sha1(jsonencode(aws_api_gateway_rest_api.api_gateway_rest_api.body))
    resource_change = "${md5(file("${path.module}/api_gateway.tf"))}"
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_rest_api.api_gateway_rest_api,
    aws_cloudwatch_log_group.api_gateway_access_logs,
    aws_cloudwatch_log_group.api_gateway_execution_logs
  ]
}

resource "aws_api_gateway_stage" "api_gateway_stage" {
  deployment_id        = aws_api_gateway_deployment.api_gateway_deployment.id
  rest_api_id          = aws_api_gateway_rest_api.api_gateway_rest_api.id
  stage_name           = "production"
  xray_tracing_enabled = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_access_logs.arn
    format = jsonencode({
      requestid : "$context.requestId",
      ip : "$context.identity.sourceIp",
      user_agent : "$context.identity.userAgent",
      request_time : "$context.requestTime",
      http_method : "$context.httpMethod",
      path : "$context.path",
      status : "$context.status",
      protocol : "$context.protocol",
      response_length : "$context.responseLength",
      x_correlationid : "$context.authorizer.x-correlation-id",
      nhsd_correlationid : "$context.authorizer.nhsd-correlation-id"
      environment : terraform.workspace
    })
  }

  depends_on = [
    aws_api_gateway_deployment.api_gateway_deployment,
    aws_api_gateway_rest_api.api_gateway_rest_api,
    aws_cloudwatch_log_group.api_gateway_access_logs,
    aws_cloudwatch_log_group.api_gateway_execution_logs
  ]
}

resource "aws_api_gateway_method_settings" "api_gateway_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  stage_name  = aws_api_gateway_stage.api_gateway_stage.stage_name
  method_path = "*/*"
  settings {
    logging_level      = "INFO"
    data_trace_enabled = true
  }

  depends_on = [
    aws_api_gateway_rest_api.api_gateway_rest_api,
    aws_api_gateway_stage.api_gateway_stage
  ]
}

resource "aws_api_gateway_gateway_response" "api_access_denied" {
  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
  response_type = "ACCESS_DENIED"
  response_templates = {
    "application/json" = jsonencode({
      errors : [{
        code : "PROCESSING"
        message : "$context.authorizer.error"
      }]
    })
  }
  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin" = "'*'"
  }
}

resource "aws_api_gateway_gateway_response" "api_default_4xx" {
  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
  response_type = "DEFAULT_4XX"
  response_templates = {
    "application/json" = jsonencode({
      errors : [{
        code : "PROCESSING"
        message : "$context.error.message"
      }]
  }) }
  response_parameters = { "gatewayresponse.header.Access-Control-Allow-Origin" = "'*'"
  }
}

resource "aws_api_gateway_gateway_response" "api_default_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
  response_type = "DEFAULT_5XX"
  response_templates = {
    "application/json" = jsonencode({
      errors : [{
        code : "PROCESSING"
        message : "exception"
      }]
  }) }
  response_parameters = { "gatewayresponse.header.Access-Control-Allow-Origin" = "'*'"
  }
}
