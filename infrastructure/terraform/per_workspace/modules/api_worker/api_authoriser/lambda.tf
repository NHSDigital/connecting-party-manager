module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.lambda_name
  description   = "authoriser lambda function"
  handler       = "api.authoriser.index.handler"
  runtime       = var.python_version

  create_package         = false
  local_existing_package = var.source_path

  tags = {
    Name = "authoriser"
  }

  layers = var.layers

}
