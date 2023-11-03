module "kms" {
  source  = "terraform-aws-modules/kms/aws"
  version = "2.0.1"

  deletion_window_in_days = local.kms.deletion_window_in_days

  description = "${title(var.name)}--cloudwatch KMS key"

  key_statements = {
    statement = {
      principals = {
        principal = {
          type = "Service"

          identifiers = [
            "logs.eu-west-2.amazonaws.com"
          ]
        }
      }
      actions = [
        "kms:Encrypt*",
        "kms:Decrypt*",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:Describe*"
      ]
      resources = ["*"]
      conditions = {
        condition = {
          test     = "ArnLike"
          variable = "kms:EncryptionContext:aws:logs:arn"
          values = [
            "arn:aws:logs:eu-west-2:${var.assume_account}:log-group:*"
          ]
        }
      }
    }
  }

  # Aliases
  aliases = ["alias/${var.name}--cloudwatch"]

  tags = {
    Name = replace("${var.name}--cloudwatch", "_", "-")
  }
}
