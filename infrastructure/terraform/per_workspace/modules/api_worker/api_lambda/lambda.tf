module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.lambda_name
  description   = "${replace(var.name, "_", "-")} lambda function"
  handler       = "api.${var.name}.index.handler"
  runtime       = var.python_version
  timeout       = 10

  allowed_triggers      = var.allowed_triggers
  environment_variables = var.environment_variables

  create_package         = false
  local_existing_package = var.source_path

  tags = {
    Name = replace(var.name, "_", "-")
  }

  layers = var.layers

  trusted_entities   = var.trusted_entities
  attach_policy_json = var.attach_policy_json
  policy_json        = var.policy_json
}
