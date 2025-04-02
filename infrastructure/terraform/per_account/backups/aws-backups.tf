data "aws_secretsmanager_secret" "source_account_id_prod" {
  name = "backups-source-account-id-prod"
}

data "aws_secretsmanager_secret_version" "source_account_id_prod" {
  secret_id = data.aws_secretsmanager_secret.source_account_id_prod.id
}

data "aws_secretsmanager_secret" "source_account_id_dev" {
  name = "backups-source-account-id-dev"
}

data "aws_secretsmanager_secret_version" "source_account_id_dev" {
  secret_id = data.aws_secretsmanager_secret.source_account_id_dev.id
}


# We need a key for the backup vaults. This key will be used to encrypt the backups themselves.
# We need one per vault (on the assumption that each vault will be in a different account).
resource "aws_kms_key" "destination_backup_key" {
  description             = "KMS key for AWS Backup vaults"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

module "destination_prod" {
  source = "../modules/aws-backup-destination"

  source_account_name     = "prod" # please note that the assigned value would be the prefix in aws_backup_vault.vault.name - change to dev/prod
  account_id              = var.assume_account
  source_account_id       = data.aws_secretsmanager_secret_version.source_account_id_prod.secret_string
  kms_key                 = aws_kms_key.destination_backup_key.arn
  enable_vault_protection = false
}

###
# Destination vault ARN output
###

output "destination_vault_arn_prod" {
  # The ARN of the backup vault in the destination account is needed by
  # the source account to copy backups into it.
  value = module.destination_prod.vault_arn
}


module "destination_dev" {
  source = "../modules/aws-backup-destination"

  source_account_name     = "dev" # please note that the assigned value would be the prefix in aws_backup_vault.vault.name - change to dev/prod
  account_id              = var.assume_account
  source_account_id       = data.aws_secretsmanager_secret_version.source_account_id_dev.secret_string
  kms_key                 = aws_kms_key.destination_backup_key.arn
  enable_vault_protection = false
}

###
# Destination vault ARN output
###

output "destination_vault_arn_dev" {
  # The ARN of the backup vault in the destination account is needed by
  # the source account to copy backups into it.
  value = module.destination_dev.vault_arn
}
