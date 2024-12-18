# module "notify_slack" {
#   source  = "terraform-aws-modules/notify-slack/aws"
#   version = "~> 5.0"
#
#   sns_topic_name = "billing-alert-slack-topic"
#
#   slack_webhook_url = "https://hooks.slack.com/services/AAA/BBB/CCC"
#   slack_channel     = "aws-notification"
#   slack_username    = "reporter"
# }

resource "aws_budgets_budget" "billing_alert_10" {
  name         = "budget-10-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 10
    threshold_type      = "PERCENTAGE"
    notification_type   = "ACTUAL"
    # subscriber_email_addresses = var.email_subscribers
    subscriber_sns_topic_arns = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_sns_topic_arns = module.notify_slack.slack_topic_arn
  }
}

resource "aws_budgets_budget" "billing_alert_50" {
  name         = "budget-50-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator = "EQUAL_TO"
    threshold           = 50
    threshold_type      = "PERCENTAGE"
    notification_type   = "ACTUAL"
    # subscriber_email_addresses = var.email_subscribers
    subscriber_sns_topic_arns = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_sns_topic_arns = module.notify_slack.slack_topic_arn
  }
}

resource "aws_budgets_budget" "billing_alert_75" {
  name         = "budget-75-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator       = "EQUAL_TO"
    threshold                 = 75
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_sns_topic_arns = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_email_addresses = var.email_subscribers
    # subscriber_sns_topic_arns  = module.notify_slack.slack_topic_arn
  }
}

resource "aws_budgets_budget" "billing_alert_90" {
  name         = "budget-590-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator       = "EQUAL_TO"
    threshold                 = 90
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_sns_topic_arns = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_email_addresses = var.email_subscribers
    # subscriber_sns_topic_arns  = module.notify_slack.slack_topic_arn
  }
}

resource "aws_budgets_budget" "billing_alert_100" {
  name         = "budget-100-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator       = "EQUAL_TO"
    threshold                 = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_sns_topic_arns = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_email_addresses = var.email_subscribers
    # subscriber_sns_topic_arns  = module.notify_slack.slack_topic_arn
  }
}
