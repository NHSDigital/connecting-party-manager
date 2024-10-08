


module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = "${var.workspace_prefix}--${var.etl_name}--${var.trigger_name}"
  description   = "${replace(var.workspace_prefix, "_", "-")} ${var.etl_name} (${var.trigger_name}) trigger lambda function"
  handler       = "etl.sds.trigger.${var.trigger_name}.${var.trigger_name}.handler"
  runtime       = var.python_version
  timeout       = 120

  timeouts = {
    create = "5m"
    update = "5m"
    delete = "5m"
  }

  create_current_version_allowed_triggers = false
  allowed_triggers                        = var.allowed_triggers

  environment_variables = merge({
    NOTIFY_LAMBDA_ARN = var.notify_lambda_arn
    },
    var.environment_variables
  )

  create_package         = false
  local_existing_package = "${path.root}/../../../src/etl/sds/trigger/${var.trigger_name}/dist/${var.trigger_name}.zip"

  tags = {
    Name = "${var.workspace_prefix}--${var.etl_name}--${var.trigger_name}"
  }

  layers = [var.etl_layer_arn, var.event_layer_arn, var.third_party_layer_arn, var.sds_layer_arn, var.domain_layer_arn]

  vpc_subnet_ids         = var.vpc_subnet_ids
  vpc_security_group_ids = var.vpc_security_group_ids

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
          "s3:PutObjectVersionTagging"
        ],
        "Effect" : "Allow",
        "Resource" : ["${var.etl_bucket_arn}", "${var.etl_bucket_arn}/*"]
      },
      {
        "Action" : [
          "s3:DeleteObject"
        ],
        "Effect" : "Allow",
        "Resource" : ["${var.etl_bucket_arn}/bulk-trigger/*ldif"]
      },
      {
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Effect" : "Allow",
        "Resource" : ["${var.notify_lambda_arn}"]
      },
      {
        "Action" : [
          "dynamodb:Scan"
        ],
        "Effect" : "Allow",
        "Resource" : ["${var.table_arn}"]
      },
      {
        "Action" : [
          "kms:Decrypt"
        ],
        "Effect" : "Allow",
        "Resource" : ["*"]
      },
      {
        "Action" : [
          "sqs:SendMessage"
        ],
        "Effect" : "Allow",
        "Resource" : ["${var.sqs_queue_arn}"]
      }
    ], var.extra_policies)
  })
}
