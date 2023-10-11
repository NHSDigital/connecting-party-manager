module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = var.lambda_name
  description   = "${replace(var.name, "_", "-")} lambda function"
  handler       = "src.api.${var.name}.index.handler"
  runtime       = var.python_version

  source_path = "${path.module}/../../../../../src/api/${var.name}/dist/${var.name}.zip"

  tags = {
    Name = replace(var.name, "_", "-")
  }

  # layers = [
  #   module.
  # ]

}
