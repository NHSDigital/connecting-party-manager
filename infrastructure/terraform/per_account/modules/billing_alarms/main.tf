resource "aws_budgets_budget" "billing_alert_50" {
  name         = "budget-50-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "EQUAL_TO"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.email_subscribers
  }

  tags = {
    Environment = var.environment
  }
}

resource "aws_budgets_budget" "billing_alert_75" {
  name         = "budget-75-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "EQUAL_TO"
    threshold                  = 75
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.email_subscribers
  }

  tags = {
    Environment = var.environment
  }
}

resource "aws_budgets_budget" "billing_alert_90" {
  name         = "budget-590-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "EQUAL_TO"
    threshold                  = 90
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.email_subscribers
  }

  tags = {
    Environment = var.environment
  }
}

resource "aws_budgets_budget" "billing_alert_100" {
  name         = "budget-100-monthly"
  budget_type  = "COST"
  limit_amount = var.limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "EQUAL_TO"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.email_subscribers
  }

  tags = {
    Environment = var.environment
  }
}
