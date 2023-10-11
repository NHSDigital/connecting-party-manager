module "lambda_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  create_layer = true

  layer_name          = var.layer_name
  description         = "${replace(var.name, "_", "-")} lambda layer"
  compatible_runtimes = [var.python_version]

  source_path = "${path.module}/../../../../../../src/layers/${var.name}/dist/${var.name}.zip"

  tags = {
    Name = replace(var.name, "_", "-")
  }
}
