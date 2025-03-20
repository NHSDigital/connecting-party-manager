module "dynamodb_table" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "3.3.0"

  name                        = var.name
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = var.hash_key
  range_key                   = var.range_key
  deletion_protection_enabled = var.deletion_protection_enabled
  attributes                  = var.attributes
  global_secondary_indexes    = var.global_secondary_indexes

  server_side_encryption_enabled     = true
  server_side_encryption_kms_key_arn = module.kms.key_arn

  point_in_time_recovery_enabled = true

  tags = merge(
    {
      Name = var.name
    },
    var.environment == "dev" ? {
      "NHSE-Enable-Backup" = "True"
    } : {}
  )

}
