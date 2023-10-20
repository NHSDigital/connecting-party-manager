module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.lambda_name
  description   = "${replace(var.name, "_", "-")} lambda function"
  handler       = "api.${var.name}.index.handler"
  runtime       = var.python_version
  environment_variables = {
    SOMETHING = "hiya"
  }
  create_package         = false
  local_existing_package = var.source_path

  tags = {
    Name = replace(var.name, "_", "-")
  }

  layers = var.layers

}
