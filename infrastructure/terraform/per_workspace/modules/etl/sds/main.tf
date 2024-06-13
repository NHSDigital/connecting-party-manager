module "bucket" {
  source                                = "terraform-aws-modules/s3-bucket/aws"
  version                               = "3.15.2"
  bucket                                = "${lower(var.workspace_prefix)}--${local.etl_name}--etl"
  attach_deny_insecure_transport_policy = true
  attach_access_log_delivery_policy     = true
  force_destroy                         = true
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
                "Resource": ["${var.table_arn}", "${var.table_arn}/*"]
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
  source = "./notify/"

  etl_name         = local.etl_name
  assume_account   = var.assume_account
  workspace_prefix = var.workspace_prefix
  python_version   = var.python_version
}

resource "aws_cloudwatch_log_group" "step_function" {
  name = "/aws/vendedlogs/states/${var.workspace_prefix}--${local.etl_name}"
}

module "update_transform_and_load_step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "4.2.0"

  type                              = "STANDARD"
  name                              = "${var.workspace_prefix}--${local.etl_name}--update-transform-and-load"
  use_existing_cloudwatch_log_group = true
  cloudwatch_log_group_name         = aws_cloudwatch_log_group.step_function.name

  definition = templatefile(
    "${path.module}/etl-diagram--update-transform-and-load.asl.json",
    {
      transform_worker_arn = module.worker_transform.arn
      load_worker_arn      = module.worker_load.arn
      etl_bucket           = module.bucket.s3_bucket_id
      changelog_key        = var.changelog_key
      etl_state_lock_key   = var.etl_state_lock_key
    }
  )

  service_integrations = {
    lambda = {
      lambda = [
        module.worker_transform.arn,
        module.worker_load.arn,
        "${module.worker_transform.arn}:*",
        "${module.worker_load.arn}:*"
      ]
    }
  }



  attach_policy_json = true
  policy_json        = <<-EOT
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
                "s3:PutObjectVersionTagging",
                "s3:DeleteObject"
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
    Name = "${var.workspace_prefix}--${local.etl_name}--update-transform-and-load"
  }

  depends_on = [aws_cloudwatch_log_group.step_function]
}

resource "aws_sfn_state_machine" "state_machine" {
  name     = "${var.workspace_prefix}--${local.etl_name}"
  type     = "STANDARD"
  role_arn = aws_iam_role.step_function.arn
  definition = templatefile(
    "${path.module}/etl-diagram.asl.json",
    {
      extract_worker_arn           = module.worker_extract.arn
      transform_worker_arn         = module.worker_transform.arn
      load_worker_arn              = module.worker_load.arn
      notify_arn                   = module.notify.arn
      etl_bucket                   = module.bucket.s3_bucket_id
      changelog_key                = var.changelog_key
      bulk_load_chunksize          = var.bulk_load_chunksize
      etl_update_state_machine_arn = module.update_transform_and_load_step_function.state_machine_arn
      etl_state_lock_key           = var.etl_state_lock_key
    }
  )
  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.step_function.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }


  tags = {
    Name = "${var.workspace_prefix}--${local.etl_name}"
  }
  depends_on = [aws_cloudwatch_log_group.step_function, module.update_transform_and_load_step_function, aws_iam_role.step_function]
}


module "trigger_bulk" {
  source = "./trigger/"

  trigger_name          = "bulk"
  etl_name              = local.etl_name
  workspace_prefix      = var.workspace_prefix
  python_version        = var.python_version
  event_layer_arn       = var.event_layer_arn
  third_party_layer_arn = var.third_party_core_layer_arn
  sds_layer_arn         = var.sds_layer_arn
  etl_bucket_arn        = module.bucket.s3_bucket_arn
  etl_layer_arn         = module.etl_layer.lambda_layer_arn
  notify_lambda_arn     = module.notify.arn
  state_machine_arn     = aws_sfn_state_machine.state_machine.arn
  table_arn             = var.table_arn
  sqs_queue_arn         = module.proxy_lambda_executor.sqs_queue_arn
  environment_variables = {
    TABLE_NAME    = var.table_name
    SQS_QUEUE_URL = module.proxy_lambda_executor.sqs_queue_url
  }
  allowed_triggers = {
    "${replace(var.workspace_prefix, "_", "-")}--AllowExecutionFromS3--${local.etl_name}--bulk" = {
      service    = "s3"
      source_arn = "${module.bucket.s3_bucket_arn}/${local.bulk_trigger_prefix}/*"
    }
  }
}

data "aws_subnets" "lambda-connectivity-private" {
  filter {
    name   = "tag:Name"
    values = ["${local.project}-lambda-connectivity-private-${var.environment}"]
  }
}

data "aws_security_groups" "sds-ldap" {
  filter {
    name   = "tag:Name"
    values = ["${local.project}-sds-ldap-${var.environment}"]
  }
}

data "aws_secretsmanager_secret_version" "ldap_host" {
  secret_id = "${var.environment}-ldap-host"
}
data "aws_secretsmanager_secret_version" "ldap_changelog_user" {
  secret_id = "${var.environment}-ldap-changelog-user"
}
data "aws_secretsmanager_secret_version" "ldap_changelog_password" {
  secret_id = "${var.environment}-ldap-changelog-password"
}

module "trigger_update" {
  source = "./trigger/"

  trigger_name          = "update"
  etl_name              = local.etl_name
  workspace_prefix      = var.workspace_prefix
  python_version        = var.python_version
  event_layer_arn       = var.event_layer_arn
  third_party_layer_arn = var.third_party_sds_update_layer_arn
  sds_layer_arn         = var.sds_layer_arn
  etl_bucket_arn        = module.bucket.s3_bucket_arn
  etl_layer_arn         = module.etl_layer.lambda_layer_arn
  notify_lambda_arn     = module.notify.arn
  state_machine_arn     = aws_sfn_state_machine.state_machine.arn
  table_arn             = var.table_arn
  sqs_queue_arn         = module.proxy_lambda_executor.sqs_queue_arn
  allowed_triggers      = {}
  environment_variables = {
    # prepend '/opt/python' (the root path of the layer) to LD_LIBRARY_PATH so that
    # all compiled dependencies can find each other. Note: this is a hack - and
    # may result in version mismatches between system libs on the lambda. The stable
    # alternative is to run or deploy the service from a container.
    LD_LIBRARY_PATH         = "/opt/python:/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/opt/lib"
    TRUSTSTORE_BUCKET       = var.truststore_bucket.id
    CPM_FQDN                = "cpm.thirdparty.nhs.uk"
    LDAP_HOST               = data.aws_secretsmanager_secret_version.ldap_host.secret_string
    LDAP_CHANGELOG_USER     = data.aws_secretsmanager_secret_version.ldap_changelog_user.secret_string
    LDAP_CHANGELOG_PASSWORD = data.aws_secretsmanager_secret_version.ldap_changelog_password.secret_string
    ETL_BUCKET              = module.bucket.s3_bucket_id
    SQS_QUEUE_URL           = module.proxy_lambda_executor.sqs_queue_url
  }

  vpc_subnet_ids         = data.aws_subnets.lambda-connectivity-private.ids
  vpc_security_group_ids = data.aws_security_groups.sds-ldap.ids
  extra_policies = [
    {
      "Action" : [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ],
      "Effect" : "Allow",
      "Resource" : concat(
        data.aws_security_groups.sds-ldap.arns
      )
    },
    {
      "Sid" : "AWSLambdaVPCAccessExecutionPermissions",
      "Effect" : "Allow",
      "Action" : [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DescribeSubnets",
        "ec2:DeleteNetworkInterface",
        "ec2:AssignPrivateIpAddresses",
        "ec2:UnassignPrivateIpAddresses"
      ],
      "Resource" : "*"
    },
    {
      "Action" : [
        "s3:GetObject"
      ],
      "Effect" : "Allow",
      "Resource" : ["${var.truststore_bucket.arn}/*"]
    }
  ]
}

module "schedule_trigger_update" {
  source      = "./schedule/"
  lambda_arn  = module.trigger_update.lambda_function.lambda_function_arn
  lambda_name = module.trigger_update.lambda_function.lambda_function_name
  # schedule_expression = var.is_persistent ? "rate(15 minutes)" : "rate(1 day)"
  schedule_expression = var.is_persistent ? "cron(0 0 1 1 ? 2000)" : "rate(1 day)" # cron(0 0 1 1 ? 2000) means "never"
}

module "bulk_trigger_notification" {
  source        = "../bucket_notification"
  target_lambda = module.trigger_bulk.lambda_function
  source_bucket = module.bucket
  filter_prefix = "${local.bulk_trigger_prefix}/"
  filter_suffix = ".ldif"
}

module "proxy_lambda_executor" {
  source = "./proxy-executor/"

  executor_name         = "input"
  etl_name              = local.etl_name
  workspace_prefix      = var.workspace_prefix
  python_version        = var.python_version
  event_layer_arn       = var.event_layer_arn
  third_party_layer_arn = var.third_party_sds_update_layer_arn
  sds_layer_arn         = var.sds_layer_arn
  etl_bucket_arn        = module.bucket.s3_bucket_arn
  etl_layer_arn         = module.etl_layer.lambda_layer_arn
  notify_lambda_arn     = module.notify.arn
  state_machine_arn     = aws_sfn_state_machine.state_machine.arn
  table_arn             = var.table_arn
  allowed_triggers      = {}
  environment_variables = {
    # prepend '/opt/python' (the root path of the layer) to LD_LIBRARY_PATH so that
    # all compiled dependencies can find each other. Note: this is a hack - and
    # may result in version mismatches between system libs on the lambda. The stable
    # alternative is to run or deploy the service from a container.
    LD_LIBRARY_PATH         = "/opt/python:/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/opt/lib"
    TRUSTSTORE_BUCKET       = var.truststore_bucket.id
    CPM_FQDN                = "cpm.thirdparty.nhs.uk"
    LDAP_HOST               = data.aws_secretsmanager_secret_version.ldap_host.secret_string
    LDAP_CHANGELOG_USER     = data.aws_secretsmanager_secret_version.ldap_changelog_user.secret_string
    LDAP_CHANGELOG_PASSWORD = data.aws_secretsmanager_secret_version.ldap_changelog_password.secret_string
    ETL_BUCKET              = module.bucket.s3_bucket_id

  }
  extra_policies = []
}
