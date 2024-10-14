resource "aws_cloudwatch_metric_alarm" "account_billing_alarm" {
  alarm_name         = "${var.prefix}--billing-alarm--${var.threshold_dollars}--${var.metric_name}"
  alarm_description  = "Billing Alarm of ${var.threshold_dollars} USD (${var.metric_name})"
  namespace          = "AWS/Billing"
  treat_missing_data = "ignore"
  tags               = var.tags

  # If statistic(metric) >= threshold in dollars then trigger topic
  metric_name         = var.metric_name
  comparison_operator = "GreaterThanOrEqualToThreshold"
  threshold           = var.threshold_dollars
  alarm_actions       = [aws_sns_topic.sns_alert_topic.arn]

  # Evaluate a new statistic(metric) every 6 hours
  period = 6 * 60 * 60 # seconds

  # Calculate statistic(metric) over the specified number evaluation periods
  statistic           = var.metric_statistic
  evaluation_periods  = var.metric_number_of_evaluation_periods
  datapoints_to_alarm = 1
}


resource "aws_sns_topic" "sns_alert_topic" {
  name = "${var.prefix}--billing-alarm-${var.threshold_dollars}--${var.metric_name}"
  tags = var.tags
}

resource "aws_sns_topic_subscription" "email_target" {
  count     = length(var.recipients)
  topic_arn = aws_sns_topic.sns_alert_topic.arn
  protocol  = "email"
  endpoint  = var.recipients[count.index]
}
