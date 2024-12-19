resource "aws_ssm_parameter" "billing_alert_subscribers" {
  name  = "${var.project}-billing-subscribers"
  type  = "StringList"
  value = "james.linnell@burendo.com,rowan.gill1@nhs.net,warran.mavrodaris2@nhs.net"
}

data "aws_ssm_parameter" "billing_alert_subscribers" {
  name = aws_ssm_parameter.billing_alert_subscribers.name
}

resource "aws_budgets_budget" "cpm_budget" {
  name         = "${var.project}-monthly-budget-${var.environment}"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = split(",", data.aws_ssm_parameter.billing_alert_subscribers.value)
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 75
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = split(",", data.aws_ssm_parameter.billing_alert_subscribers.value)
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 90
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = split(",", data.aws_ssm_parameter.billing_alert_subscribers.value)
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = split(",", data.aws_ssm_parameter.billing_alert_subscribers.value)
  }
}
