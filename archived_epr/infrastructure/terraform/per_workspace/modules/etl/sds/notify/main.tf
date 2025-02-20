data "aws_secretsmanager_secret" "slack_webhook_url" {
  name  = "${terraform.workspace}--etl-notify-slack-webhook-url"
  count = contains(["dev", "ref", "int", "qa", "prod"], terraform.workspace) ? 1 : 0
}

data "aws_secretsmanager_secret_version" "slack_webhook_url" {
  count     = length((data.aws_secretsmanager_secret.slack_webhook_url))
  secret_id = data.aws_secretsmanager_secret.slack_webhook_url.*.id[0]
}

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
  layers                 = [var.etl_layer_arn, var.event_layer_arn, var.third_party_layer_arn]

  environment_variables = {
    SLACK_WEBHOOK_URL = concat(data.aws_secretsmanager_secret_version.slack_webhook_url.*.secret_string, ["http://example.com"])[0]
    WORKSPACE         = terraform.workspace
    ENVIRONMENT       = var.environment
  }

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
