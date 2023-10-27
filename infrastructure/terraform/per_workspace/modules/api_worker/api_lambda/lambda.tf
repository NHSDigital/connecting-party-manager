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

}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGateway-${module.lambda_function.lambda_function_name}"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.apigateway_execution_arn}/*/*/*"

  depends_on = [
    module.lambda_function.lambda_function_arn
  ]
}
