module "sqs" {
  source = "terraform-aws-modules/sqs/aws"

  name = "${var.workspace_prefix}--${var.etl_name}--${var.executor_name}-sqs"

  fifo_queue                 = true
  visibility_timeout_seconds = 120

}

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = "${var.workspace_prefix}--${var.etl_name}--${var.executor_name}"
  description   = "${replace(var.workspace_prefix, "_", "-")} ${var.etl_name} (${var.executor_name}) executor lambda function"
  handler       = "etl.sds.executor.${var.executor_name}.${var.executor_name}.handler"
  runtime       = var.python_version
  timeout       = 120

  timeouts = {
    create = "5m"
    update = "5m"
    delete = "5m"
  }

  event_source_mapping = {
    sqs = {
      event_source_arn        = module.sqs.queue_arn
      function_response_types = ["ReportBatchItemFailures"]
      batch_size              = 1
      scaling_config = {
        maximum_concurrency = 2
      }
    }
  }

  create_current_version_allowed_triggers = false
  allowed_triggers                        = var.allowed_triggers

  environment_variables = merge({
    STATE_MACHINE_ARN = var.state_machine_arn
    NOTIFY_LAMBDA_ARN = var.notify_lambda_arn
    },
    var.environment_variables
  )

  create_package         = false
  local_existing_package = "${path.root}/../../../src/etl/sds/executor/${var.executor_name}/dist/${var.executor_name}.zip"

  tags = {
    Name = "${var.workspace_prefix}--${var.etl_name}--${var.executor_name}"
  }

  layers = [var.etl_layer_arn, var.event_layer_arn, var.third_party_layer_arn, var.sds_layer_arn]

  trusted_entities = [
    {
      type = "Service",
      identifiers = [
        "s3.amazonaws.com"
      ]
    }
  ]

  attach_policy_json = true
  policy_json = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : concat([
      {
        "Action" : [
          "s3:PutObject",
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:PutObjectVersionTagging",
          "s3:DeleteObject"
        ],
        "Effect" : "Allow",
        "Resource" : ["${var.etl_bucket_arn}", "${var.etl_bucket_arn}/*"]
      },
      {
        "Action" : [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        "Effect" : "Allow",
        "Resource" : ["${module.sqs.queue_arn}"]
      },
      {
        "Action" : [
          "states:StartExecution",
          "states:DescribeExecution"
        ],
        "Effect" : "Allow",
        "Resource" : ["${var.state_machine_arn}"]
      },
      {
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Effect" : "Allow",
        "Resource" : ["${var.notify_lambda_arn}"]
      },
    ], var.extra_policies)
  })
}
