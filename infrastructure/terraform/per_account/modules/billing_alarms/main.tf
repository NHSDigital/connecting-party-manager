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

resource "aws_budgets_budget" "cpm_budget" {
  name         = "nhse-cpm-monthly-budget"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.email_subscribers
    subscriber_sns_topic_arns  = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_sns_topic_arns = module.notify_slack.slack_topic_arn
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 75
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.email_subscribers
    subscriber_sns_topic_arns  = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_sns_topic_arns = module.notify_slack.slack_topic_arn
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 90
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.email_subscribers
    subscriber_sns_topic_arns  = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_sns_topic_arns = module.notify_slack.slack_topic_arn
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.email_subscribers
    subscriber_sns_topic_arns  = ["arn:aws:sns:eu-west-2:660842439611:test-dev-billing-alarm"]
    # subscriber_sns_topic_arns = module.notify_slack.slack_topic_arn
  }
}
