module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.lambda_name
  description   = "${replace(var.name, "_", "-")} lambda function"
  handler       = "api.authoriser.index.handler"
  runtime       = var.python_version

  create_package         = false
  local_existing_package = var.source_path

  # allowed_triggers = {
  #   APIGatewayAny = {
  #     service    = "apigateway"
  #     source_arn = "arn:aws:execute-api:eu-west-1:135367859851:aqnku8akd0/*/*/*"
  #   }
  # }

  tags = {
    Name = replace(var.name, "_", "-")
  }

  layers = var.layers

  trusted_entities   = var.trusted_entities
  attach_policy_json = var.attach_policy_json
  policy_json        = var.policy_json
}
