module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.lambda_name
  description   = "${replace(var.name, "_", "-")} lambda function"
  handler       = "api.authoriser.index.handler"
  runtime       = var.python_version

  create_package         = false
  local_existing_package = var.source_path

  tags = {
    Name = replace(var.name, "_", "-")
  }

  layers = var.layers

  assume_role_policy_statements = var.assume_role_policy_statements
  attach_policy_statements      = var.attach_policy_statements
  policy_statements             = var.policy_statements
  trusted_entities              = var.trusted_entities

}
