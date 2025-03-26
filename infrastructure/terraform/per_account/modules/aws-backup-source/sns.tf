resource "aws_sns_topic" "backup" {
  name              = "${local.resource_name_prefix}-notifications"
  kms_master_key_id = var.bootstrap_kms_key_arn
  policy            = data.aws_iam_policy_document.allow_backup_to_sns.json
}

data "aws_iam_policy_document" "allow_backup_to_sns" {
  policy_id = "backup"

  statement {
    actions = [
      "SNS:Publish",
    ]

    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["backup.amazonaws.com"]
    }

    resources = ["*"]

    sid = "allow_backup"
  }
}

resource "aws_sns_topic_subscription" "aws_backup_notifications_lambda_target" {
  topic_arn     = aws_sns_topic.backup.arn
  protocol      = "lambda"
  endpoint      = var.notify_lambda_arn
  filter_policy = jsonencode({ "State" : [{ "anything-but" : "COMPLETED" }] })
}
