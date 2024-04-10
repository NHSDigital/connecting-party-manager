module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = "${var.workspace_prefix}--${var.etl_name}--notify"
  description   = "${replace(var.workspace_prefix, "_", "-")} ${var.etl_name} (notify) lambda function"
  handler       = "etl.notify.notify.handler"
  runtime       = var.python_version
  timeout       = 10

  timeouts = {
    create = "5m"
    update = "5m"
    delete = "5m"
  }

  create_current_version_allowed_triggers = false
  allowed_triggers = {
    "${replace(var.workspace_prefix, "_", "-")}--AllowExecutionFromStepFunction--${var.etl_name}--notify" = {
      service    = "states"
      source_arn = "arn:aws:states:eu-west-2:${var.assume_account}:stateMachine:${var.workspace_prefix}--${var.etl_name}"
    }
  }


  create_package         = false
  local_existing_package = "${path.root}/../../../src/etl/notify/dist/notify.zip"

  tags = {
    Name = "${var.workspace_prefix}--${var.etl_name}--notify"
  }

  trusted_entities = [
    {
      type = "Service",
      identifiers = [
        "states.amazonaws.com"
      ]
    }
  ]
}
