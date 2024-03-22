module "bucket" {
  source        = "terraform-aws-modules/s3-bucket/aws"
  version       = "3.15.2"
  bucket        = "${lower(var.workspace_prefix)}--${local.etl_name}--etl"
  force_destroy = true
  versioning = {
    enabled = true
  }
  tags = {
    Name = "${var.workspace_prefix}--${local.etl_name}--bucket"
  }
}

module "etl_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  layer_name             = "${var.workspace_prefix}--${local.etl_name}--etl_utils"
  description            = "ETL Utils lambda layer"
  create_layer           = true
  compatible_runtimes    = [var.python_version]
  create_package         = false
  local_existing_package = "${path.root}/../../../src/layers/etl_utils/dist/etl_utils.zip"

  tags = {
    Name = "${var.workspace_prefix}--${local.etl_name}--etl_utils"
  }
}


module "sds_layer" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  layer_name             = "${var.workspace_prefix}--${local.etl_name}--sds"
  description            = "SDS domain lambda layer"
  create_layer           = true
  compatible_runtimes    = [var.python_version]
  create_package         = false
  local_existing_package = "${path.root}/../../../src/layers/sds/dist/sds.zip"

  tags = {
    Name = "${var.workspace_prefix}--${local.etl_name}--sds"
  }
}

module "worker_extract" {
  source = "./worker/"

  etl_stage        = "extract"
  etl_name         = local.etl_name
  assume_account   = var.assume_account
  workspace_prefix = var.workspace_prefix
  python_version   = var.python_version
  etl_bucket_name  = module.bucket.s3_bucket_id
  etl_bucket_arn   = module.bucket.s3_bucket_arn
  layers           = [var.event_layer_arn, var.third_party_core_layer_arn, module.etl_layer.lambda_layer_arn, module.sds_layer.lambda_layer_arn]

  policy_json = <<-EOT
      {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:PutObject",
                    "s3:AbortMultipartUpload",
                    "s3:GetBucketLocation",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:PutObjectVersionTagging"
                ],
                "Effect": "Allow",
                "Resource": ["${module.bucket.s3_bucket_arn}", "${module.bucket.s3_bucket_arn}/*"]
            }
        ]
      }
    EOT

}

module "worker_transform" {
  source = "./worker/"

  etl_stage        = "transform"
  etl_name         = local.etl_name
  assume_account   = var.assume_account
  workspace_prefix = var.workspace_prefix
  python_version   = var.python_version
  etl_bucket_name  = module.bucket.s3_bucket_id
  etl_bucket_arn   = module.bucket.s3_bucket_arn
  environment_variables = {
    TABLE_NAME = var.table_name
  }
  layers = [var.event_layer_arn, var.third_party_core_layer_arn, module.etl_layer.lambda_layer_arn, module.sds_layer.lambda_layer_arn, var.domain_layer]

  policy_json = <<-EOT
      {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:PutObject",
                    "s3:AbortMultipartUpload",
                    "s3:GetBucketLocation",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:PutObjectVersionTagging"
                ],
                "Effect": "Allow",
                "Resource": ["${module.bucket.s3_bucket_arn}", "${module.bucket.s3_bucket_arn}/*"]
            },
            {
                "Action": [
                    "dynamodb:Query"
                ],
                "Effect": "Allow",
                "Resource": ["${var.table_arn}"]
            },
            {
                "Action": [
                    "kms:Decrypt"
                ],
                "Effect": "Allow",
                "Resource": ["*"]
            }
        ]
      }
    EOT

}

module "worker_load" {
  source = "./worker/"

  etl_stage        = "load"
  etl_name         = local.etl_name
  assume_account   = var.assume_account
  workspace_prefix = var.workspace_prefix
  python_version   = var.python_version
  etl_bucket_name  = module.bucket.s3_bucket_id
  etl_bucket_arn   = module.bucket.s3_bucket_arn
  environment_variables = {
    TABLE_NAME = var.table_name
  }
  layers = [var.event_layer_arn, var.third_party_core_layer_arn, module.etl_layer.lambda_layer_arn, module.sds_layer.lambda_layer_arn, var.domain_layer]

  policy_json = <<-EOT
      {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:PutObject",
                    "s3:AbortMultipartUpload",
                    "s3:GetBucketLocation",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:PutObjectVersionTagging"
                ],
                "Effect": "Allow",
                "Resource": ["${module.bucket.s3_bucket_arn}", "${module.bucket.s3_bucket_arn}/*"]
            },
            {
                "Action": [
                    "dynamodb:PutItem"
                ],
                "Effect": "Allow",
                "Resource": ["${var.table_arn}"]
            },
            {
                "Action": [
                    "kms:Decrypt"
                ],
                "Effect": "Allow",
                "Resource": ["*"]
            }
        ]
      }
    EOT
}

module "notify" {
  source = "./../notify/"

  etl_name         = local.etl_name
  assume_account   = var.assume_account
  workspace_prefix = var.workspace_prefix
  python_version   = var.python_version
}

resource "aws_cloudwatch_log_group" "step_function" {
  name = "/aws/vendedlogs/states/${var.workspace_prefix}--${local.etl_name}"
}

module "step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "4.1.0"

  type                              = "STANDARD"
  name                              = "${var.workspace_prefix}--${local.etl_name}"
  use_existing_cloudwatch_log_group = true
  cloudwatch_log_group_name         = aws_cloudwatch_log_group.step_function.name

  definition = templatefile(
    "${path.module}/step-function.asl.json",
    {
      extract_worker_arn   = module.worker_extract.arn
      transform_worker_arn = module.worker_transform.arn
      load_worker_arn      = module.worker_load.arn
      notify_arn           = module.notify.arn
      etl_bucket           = module.bucket.s3_bucket_id
      changelog_key        = var.changelog_key
    }
  )

  service_integrations = {
    lambda = {
      lambda = [
        module.worker_extract.arn,
        module.worker_transform.arn,
        module.worker_load.arn,
        module.notify.arn
      ]
    }
  }

  attach_policy_json = true
  policy_json        = <<-EOT
    {
      "Version": "2012-10-17",
      "Statement": [
          {
            "Action": "lambda:InvokeFunction",
            "Effect": "Allow",
            "Resource": [
              "${module.worker_extract.arn}:*",
              "${module.worker_transform.arn}:*",
              "${module.worker_load.arn}:*",
              "${module.notify.arn}:*"
            ]
          },
          {
            "Action": [
                "s3:PutObject",
                "s3:AbortMultipartUpload",
                "s3:GetBucketLocation",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:PutObjectVersionTagging"
            ],
            "Effect": "Allow",
            "Resource": [
              "${module.bucket.s3_bucket_arn}",
              "${module.bucket.s3_bucket_arn}/*"
            ]
          }
      ]
    }
  EOT

  logging_configuration = {
    log_destination        = "${aws_cloudwatch_log_group.step_function.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  tags = {
    Name = "${var.workspace_prefix}--${local.etl_name}"
  }

  depends_on = [aws_cloudwatch_log_group.step_function]
}


module "trigger_bulk" {
  source = "./trigger/"

  trigger_name          = "bulk"
  etl_name              = local.etl_name
  assume_account        = var.assume_account
  workspace_prefix      = var.workspace_prefix
  python_version        = var.python_version
  event_layer_arn       = var.event_layer_arn
  third_party_layer_arn = var.third_party_core_layer_arn
  etl_bucket_arn        = module.bucket.s3_bucket_arn
  etl_layer_arn         = module.etl_layer.lambda_layer_arn
  notify_lambda_arn     = module.notify.arn
  state_machine_arn     = module.step_function.state_machine_arn
  table_arn             = var.table_arn
  table_name            = var.table_name
  allowed_triggers = {
    "${replace(var.workspace_prefix, "_", "-")}--AllowExecutionFromS3--${local.etl_name}--bulk" = {
      service    = "s3"
      source_arn = "${module.bucket.s3_bucket_arn}/${local.bulk_trigger_prefix}/*"
    }
  }
}

module "trigger_update" {
  source = "./trigger/"

  trigger_name          = "update"
  etl_name              = local.etl_name
  assume_account        = var.assume_account
  workspace_prefix      = var.workspace_prefix
  python_version        = var.python_version
  event_layer_arn       = var.event_layer_arn
  third_party_layer_arn = var.third_party_sds_update_layer_arn
  etl_bucket_arn        = module.bucket.s3_bucket_arn
  etl_layer_arn         = module.etl_layer.lambda_layer_arn
  notify_lambda_arn     = module.notify.arn
  state_machine_arn     = module.step_function.state_machine_arn
  table_arn             = var.table_arn
  table_name            = var.table_name
  allowed_triggers = {
  }
}

module "schedule_trigger_update" {
  source              = "./schedule/"
  lambda_arn          = module.trigger_update.lambda_function.lambda_function_arn
  lambda_name         = module.trigger_update.lambda_function.lambda_function_name
  schedule_expression = var.is_persistent ? "rate(15 minutes)" : "rate(1 day)"
}

module "bulk_trigger_notification" {
  source        = "../bucket_notification"
  target_lambda = module.trigger_bulk.lambda_function
  source_bucket = module.bucket
  filter_prefix = "${local.bulk_trigger_prefix}/"
  filter_suffix = ".ldif"
}
