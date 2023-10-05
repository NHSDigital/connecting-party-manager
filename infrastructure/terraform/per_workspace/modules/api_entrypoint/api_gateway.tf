module "api_gateway" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = var.name
  description   = "HTTP API Gateway for ${var.name}"
  protocol_type = "HTTP"


  # Custom domain
  domain_name = "terraform-aws-modules.modules.tf"
  #domain_name_certificate_arn = "arn:aws:acm:eu-west-1:052235179155:certificate/2b3a7ed9-05e1-4f9e-952b-27744ba06da6"

  # Access logs
  #default_stage_access_log_destination_arn = "arn:aws:logs:eu-west-1:835367859851:log-group:debug-apigateway"
  #default_stage_access_log_format          = "$context.identity.sourceIp - - [$context.requestTime] \"$context.httpMethod $context.routeKey $context.protocol\" $context.status $context.responseLength $context.requestId $context.integrationErrorMessage"

  # Routes and integrations
  #   integrations = {
  #     "POST /" = {
  #       lambda_arn             = "arn:aws:lambda:eu-west-1:052235179155:function:my-function"
  #       payload_format_version = "2.0"
  #       timeout_milliseconds   = 12000
  #     }

  #     "GET /some-route-with-authorizer" = {
  #       integration_type = "HTTP_PROXY"
  #       integration_uri  = "some url"
  #       authorizer_key   = "azure"
  #     }

  #     "$default" = {
  #       lambda_arn = "arn:aws:lambda:eu-west-1:052235179155:function:my-default-function"
  #     }
  #   }

  #   authorizers = {
  #     "azure" = {
  #       authorizer_type  = "JWT"
  #       identity_sources = "$request.header.Authorization"
  #       name             = "azure-auth"
  #       audience         = ["d6a38afd-45d6-4874-d1aa-3c5c558aqcc2"]
  #       issuer           = "https://sts.windows.net/aaee026e-8f37-410e-8869-72d9154873e4/"
  #     }
  #   }

}
