# data "aws_arn" "source_terraform_role" {
#   arn = var.source_terraform_role_arn
# }

# data "aws_caller_identity" "current" {}


# # We need a key for the backup vaults. This key will be used to encrypt the backups themselves.
# # We need one per vault (on the assumption that each vault will be in a different account).
# resource "aws_kms_key" "destination_backup_key" {
#   description             = "KMS key for AWS Backup vaults"
#   deletion_window_in_days = 7
#   enable_key_rotation     = true
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Sid    = "Enable IAM User Permissions"
#         Principal = {
#           AWS = "arn:aws:iam::${local.destination_account_id}:root"
#         }
#         Action   = "kms:*"
#         Resource = "*"
#       }
#     ]
#   })
# }

# # module "destination" {
# #   source = "../../modules/aws-backup-destination"

# #   source_account_name     = "test" # please note that the assigned value would be the prefix in aws_backup_vault.vault.name
# #   account_id              = local.destination_account_id
# #   source_account_id       = local.source_account_id
# #   kms_key                 = aws_kms_key.destination_backup_key.arn
# #   enable_vault_protection = false
# # }

# # ###
# # # Destination vault ARN output
# # ###

# # output "destination_vault_arn" {
# #   # The ARN of the backup vault in the destination account is needed by
# #   # the source account to copy backups into it.
# #   value = module.destination.vault_arn
# # }
