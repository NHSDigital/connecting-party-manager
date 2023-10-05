module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.name
  description   = "${var.name} lambda function"
  handler       = var.handler
  runtime       = var.python_version

  source_path = var.source_path

}
