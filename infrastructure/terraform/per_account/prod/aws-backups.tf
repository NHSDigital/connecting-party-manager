data "aws_secretsmanager_secret" "destination_vault_arn" {
  name = "destination_vault_arn"
}

data "aws_secretsmanager_secret_version" "destination_vault_arn" {
  secret_id = data.aws_secretsmanager_secret.destination_vault_arn.id
}

data "aws_secretsmanager_secret" "destination_account_id" {
  name = "destination_account_id"
}

data "aws_secretsmanager_secret_version" "destination_account_id" {
  secret_id = data.aws_secretsmanager_secret.destination_account_id.id
}

# First, we create an S3 bucket for compliance reports. You may already have a module for creating
# S3 buckets with more refined access rules, which you may prefer to use.

resource "aws_s3_bucket" "backup_reports" {
  bucket_prefix = "${local.project}-backup-reports"
}

# Now we have to configure access to the report bucket.

resource "aws_s3_bucket_ownership_controls" "backup_reports" {
  bucket = aws_s3_bucket.backup_reports.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "backup_reports" {
  depends_on = [aws_s3_bucket_ownership_controls.backup_reports]

  bucket = aws_s3_bucket.backup_reports.id
  acl    = "private"
}

resource "aws_s3_bucket_policy" "backup_reports_policy" {
  bucket = aws_s3_bucket.backup_reports.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${var.assume_account}:role/aws-service-role/reports.backup.amazonaws.com/AWSServiceRoleForBackupReports"
        },
        Action   = "s3:PutObject",
        Resource = "${aws_s3_bucket.backup_reports.arn}/*",
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# We need a key for the SNS topic that will be used for notifications from AWS Backup. This key
# will be used to encrypt the messages sent to the topic before they are sent to the subscribers,
# but isn't needed by the recipients of the messages.


# Now we can define the key itself
resource "aws_kms_key" "backup_notifications" {
  description             = "KMS key for AWS Backup notifications"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Sid    = "Enable IAM User Permissions"
        Principal = {
          AWS = "arn:aws:iam::${var.assume_account}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action   = ["kms:GenerateDataKey*", "kms:Decrypt"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
        Action   = ["kms:GenerateDataKey*", "kms:Decrypt"]
        Resource = "*"
      },
    ]
  })
}

resource "aws_kms_alias" "backup_notifications" {
  name          = "alias/key-for-backup-notify"
  target_key_id = aws_kms_key.backup_notifications.key_id
}

# Now we can deploy the source and destination modules, referencing the resources we've created above.

module "source" {
  source = "../modules/aws-backup-source"

  backup_copy_vault_account_id = data.aws_secretsmanager_secret_version.destination_account_id.secret_string
  backup_copy_vault_arn        = data.aws_secretsmanager_secret_version.destination_vault_arn.secret_string
  environment_name             = var.environment
  bootstrap_kms_key_arn        = aws_kms_key.backup_notifications.arn
  project_name                 = local.project
  reports_bucket               = aws_s3_bucket.backup_reports.bucket
  terraform_role_arn           = "arn:aws:iam::${var.assume_account}:role/${var.assume_role}"
  python_version               = var.python_version
  notify_lambda_arn            = module.notify.arn

  backup_plan_config_dynamodb = {
    "compliance_resource_types" : [
      "DynamoDB"
    ],
    "rules" : [
      {
        "copy_action" : {
          "delete_after" : 31
        },
        "lifecycle" : {
          "delete_after" : 4
        },
        "name" : "daily_kept_for_2_days",
        "schedule" : "cron(0 20 * * ? *)"
      }
    ],
    "enable" : true,
    "selection_tag" : "NHSE-Enable-Backup"
  }
}


module "notify" {
  source = "../modules/notify/"

  assume_account        = var.assume_account
  project_name          = local.project
  python_version        = var.python_version
  environment           = var.environment
  event_layer_arn       = element([for instance in module.layers : instance if instance.name == "event"], 0).layer_arn
  third_party_layer_arn = element([for instance in module.third_party_layers : instance if instance.name == "third_party_core"], 0).layer_arn
}
