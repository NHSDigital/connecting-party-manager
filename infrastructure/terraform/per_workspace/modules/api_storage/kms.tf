module "kms" {
  source  = "terraform-aws-modules/kms/aws"
  version = "2.0.1"

  deletion_window_in_days = var.kms_deletion_window_in_days

  # Aliases
  aliases = [var.name]
}
