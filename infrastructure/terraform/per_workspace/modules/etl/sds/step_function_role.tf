locals {
  name = "${var.workspace_prefix}--${local.etl_name}"
  tags = {
    Name = "${var.workspace_prefix}--${local.etl_name}"
  }
}

locals {
  service_integrations = {
    lambda = {
      actions = ["lambda:InvokeFunction"]
      resources = [
        module.worker_extract.arn,
        module.worker_transform.arn,
        module.worker_load.arn,
        module.notify.arn,
        "${module.worker_extract.arn}:*",
        "${module.worker_transform.arn}:*",
        "${module.worker_load.arn}:*",
        "${module.notify.arn}:*"
      ]
    }

    step_function_start = {
      actions   = ["states:StartExecution", "states:StartSyncExecution"]
      resources = [module.update_transform_and_load_step_function.state_machine_arn]
    }

    step_function_stop = {
      actions   = ["states:DescribeExecution", "states:StopExecution"]
      resources = ["${replace(module.update_transform_and_load_step_function.state_machine_arn, "stateMachine", "execution")}:*"]
    }

    step_function_event_polling = {
      actions   = ["events:PutTargets", "events:PutRule", "events:DescribeRule"]
      resources = ["arn:aws:events:eu-west-2:${var.assume_account}:rule/StepFunctionsGetEventsForStepFunctionsExecutionRule"]
    }

    s3 = {
      actions = [
        "s3:PutObject",
        "s3:AbortMultipartUpload",
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketMultipartUploads",
        "s3:PutObjectVersionTagging"
      ]
      resources = [
        "${module.bucket.s3_bucket_arn}",
        "${module.bucket.s3_bucket_arn}/*"
      ]
    }

    logging = {
      actions = [
        "logs:CreateLogDelivery",
        "logs:GetLogDelivery",
        "logs:UpdateLogDelivery",
        "logs:DeleteLogDelivery",
        "logs:ListLogDeliveries",
        "logs:PutResourcePolicy",
        "logs:DescribeResourcePolicies",
        "logs:DescribeLogGroups",
      ]
      resources = ["*"]
    }
  }

  depends_on = [module.bucket, module.update_transform_and_load_step_function]
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["states.eu-west-2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "step_function" {
  name               = "${local.name}--role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = local.tags
}

data "aws_iam_policy_document" "service" {
  for_each = { for k, v in local.service_integrations : k => v }

  dynamic "statement" {
    for_each = [each.value]
    content {
      effect    = "Allow"
      sid       = replace("${local.name}${each.key}", "/[^0-9A-Za-z]*/", "")
      actions   = each.value.actions
      resources = each.value.resources
    }
  }
}

resource "aws_iam_policy" "service" {
  for_each = { for k, v in local.service_integrations : k => v }
  name     = "${local.name}--${each.key}"
  policy   = data.aws_iam_policy_document.service[each.key].json
  tags     = local.tags
}

resource "aws_iam_policy_attachment" "service" {
  for_each   = { for k, v in local.service_integrations : k => v }
  name       = "${local.name}--${each.key}"
  roles      = [aws_iam_role.step_function.name]
  policy_arn = aws_iam_policy.service[each.key].arn
}
