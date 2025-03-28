data "aws_secretsmanager_secret" "slack_webhook_url" {
  name = "${var.environment}--etl-notify-slack-webhook-url"
}

data "aws_secretsmanager_secret_version" "slack_webhook_url" {
  secret_id = data.aws_secretsmanager_secret.slack_webhook_url.id
}
module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = "${var.project_name}--notify"
  description   = "${replace(var.project_name, "_", "-")} (notify) lambda function"
  handler       = "notify.notify.lambda_handler"
  runtime       = var.python_version
  timeout       = 10

  timeouts = {
    create = "5m"
    update = "5m"
    delete = "5m"
  }

  create_current_version_allowed_triggers = false
  allowed_triggers = {
    "${replace(var.project_name, "_", "-")}--AllowExecutionFromSNS--notify" = {
      service    = "sns"
      source_arn = "arn:aws:sns:eu-west-2:${var.assume_account}:eu-west-2-${var.assume_account}-backup-notifications"
    }
  }

  create_package         = false
  local_existing_package = "${path.root}/../../../../src/notify/dist/notify.zip"
  layers                 = [var.event_layer_arn, var.third_party_layer_arn]

  environment_variables = {
    SLACK_WEBHOOK_URL = data.aws_secretsmanager_secret_version.slack_webhook_url.secret_string
    ENVIRONMENT       = var.environment
  }

  tags = {
    Name = "${var.project_name}--notify"
  }

  trusted_entities = [
    {
      type = "Service",
      identifiers = [
        "sns.amazonaws.com"
      ]
    }
  ]
}
