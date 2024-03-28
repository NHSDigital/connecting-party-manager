resource "aws_cloudwatch_event_rule" "event_rule" {
  name                = "${var.lambda_name}--event-rule"
  description         = "Rule to trigger ${var.lambda_name}"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "event_target" {
  target_id = "${var.lambda_name}--event-target"
  rule      = aws_cloudwatch_event_rule.event_rule.name
  arn       = var.lambda_arn
}


resource "aws_lambda_permission" "allow_execution_from_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.event_rule.arn
}
