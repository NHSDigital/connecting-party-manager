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

module "layer" {
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
  etl_layer_arn         = module.layer.lambda_layer_arn
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
