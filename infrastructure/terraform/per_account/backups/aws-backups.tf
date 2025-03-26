data "aws_secretsmanager_secret" "source_account_id" {
  name = "backups-source-account-id"
}

data "aws_secretsmanager_secret_version" "source_account_id" {
  secret_id = data.aws_secretsmanager_secret.source_account_id.id
}


# We need a key for the backup vaults. This key will be used to encrypt the backups themselves.
# We need one per vault (on the assumption that each vault will be in a different account).
resource "aws_kms_key" "destination_backup_key" {
  description             = "KMS key for AWS Backup vaults"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

module "destination" {
  source = "../modules/aws-backup-destination"

  source_account_name     = "dev" # please note that the assigned value would be the prefix in aws_backup_vault.vault.name - change to dev/prod BACKUPS_LOGIC
  account_id              = var.assume_account
  source_account_id       = data.aws_secretsmanager_secret_version.source_account_id.secret_string
  kms_key                 = aws_kms_key.destination_backup_key.arn
  enable_vault_protection = false
}

###
# Destination vault ARN output
###

output "destination_vault_arn" {
  # The ARN of the backup vault in the destination account is needed by
  # the source account to copy backups into it.
  value = module.destination.vault_arn
}
