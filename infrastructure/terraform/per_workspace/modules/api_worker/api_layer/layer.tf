module "lambda_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  timeouts = {
    create = "5m"
    update = "5m"
    delete = "5m"
  }

  create_layer = true

  layer_name          = var.layer_name
  description         = "${replace(var.name, "_", "-")} lambda layer"
  compatible_runtimes = [var.python_version]

  create_package         = false
  local_existing_package = var.source_path
  environment_variables  = var.environment_variables

  tags = {
    Name = replace(var.name, "_", "-")
  }
}
