module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.lambda_name
  description   = "${replace(var.name, "_", "-")} lambda function"
  handler       = "api.${var.name}.index.handler"
  runtime       = var.python_version
  timeout       = 10
  memory_size   = var.memory_size

  timeouts = {
    create = "5m"
    update = "5m"
    delete = "5m"
  }

  create_current_version_allowed_triggers = false
  allowed_triggers                        = var.allowed_triggers
  environment_variables                   = var.environment_variables

  create_package         = false
  local_existing_package = var.source_path

  tags = {
    Name = replace(var.name, "_", "-")
  }

  layers = var.layers

  trusted_entities   = var.trusted_entities
  attach_policy_json = var.attach_policy_json
  policy_json        = var.policy_json

  attach_policy_statements = var.attach_policy_statements
  policy_statements        = var.policy_statements

  attach_network_policy              = var.vpc
  vpc_subnet_ids                     = var.subnets
  vpc_security_group_ids             = var.security_groups
  replace_security_groups_on_destroy = true
}
