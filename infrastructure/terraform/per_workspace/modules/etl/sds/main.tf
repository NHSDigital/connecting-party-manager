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

  etl_stage             = "extract"
  etl_name              = local.etl_name
  assume_account        = var.assume_account
  workspace_prefix      = var.workspace_prefix
  python_version        = var.python_version
  event_layer_arn       = var.event_layer_arn
  third_party_layer_arn = var.third_party_layer_arn
  etl_bucket_name       = module.bucket.s3_bucket_id
  etl_bucket_arn        = module.bucket.s3_bucket_arn
  etl_layer_arn         = module.etl_layer.lambda_layer_arn
  sds_layer_arn         = module.sds_layer.lambda_layer_arn
}

module "notify" {
  source = "./../notify/"

  etl_name         = local.etl_name
  assume_account   = var.assume_account
  workspace_prefix = var.workspace_prefix
  python_version   = var.python_version
}

resource "aws_cloudwatch_log_group" "step_function" {
  name = "${var.workspace_prefix}--${local.etl_name}--step-function"
}

module "step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "4.1.0"

  type = "EXPRESS"
  name = "${var.workspace_prefix}--${local.etl_name}"

  definition = templatefile(
    "${path.module}/step-function.asl.json",
    {
      extract_worker_arn = module.worker_extract.arn
      notify_arn         = module.notify.arn
      etl_bucket         = module.bucket.s3_bucket_id
      changelog_key      = var.changelog_key
    }
  )

  service_integrations = {
    lambda = {
      lambda = [module.worker_extract.arn, module.notify.arn]
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
}


module "trigger_bulk" {
  source = "./trigger/"

  trigger_name          = "bulk"
  etl_name              = local.etl_name
  assume_account        = var.assume_account
  workspace_prefix      = var.workspace_prefix
  python_version        = var.python_version
  event_layer_arn       = var.event_layer_arn
  third_party_layer_arn = var.third_party_layer_arn
  etl_bucket_arn        = module.bucket.s3_bucket_arn
  etl_layer_arn         = module.etl_layer.lambda_layer_arn
  notify_lambda_arn     = module.notify.arn
  state_machine_arn     = module.step_function.state_machine_arn
  allowed_triggers = {
    "${replace(var.workspace_prefix, "_", "-")}--AllowExecutionFromS3--${local.etl_name}--bulk" = {
      service    = "s3"
      source_arn = "${module.bucket.s3_bucket_arn}/${local.bulk_trigger_prefix}/*"
    }
  }
}


module "bulk_trigger_notification" {
  source        = "../bucket_notification"
  target_lambda = module.trigger_bulk.lambda_function
  source_bucket = module.bucket
  filter_prefix = "${local.bulk_trigger_prefix}/"
  filter_suffix = ".ldif"
}
