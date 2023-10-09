provider "aws" {
  region = local.region

  assume_role {
    role_arn = "arn:aws:iam::${var.assume_account}:role/${var.assume_role}"
  }

  default_tags {
    tags = {
      Environment = var.environment
      Timestamp   = timestamp()
      Workspace   = terraform.workspace
      Project     = local.project
    }
  }
}

module "products_table" {
  source      = "./modules/api_storage"
  name        = "${var.environment}-products-table"
  environment = var.environment
  hash_key    = "pk"
  range_key   = "sk"
  attributes = [
    {
      name = "pk"
      type = "S"
    },
    {
      name = "sk"
      type = "S"
    }
  ]
  deletion_protection_enabled = var.deletion_protection_enabled
  kms_deletion_window_in_days = 7
}

# module "api_worker_create" {
#   source = "./modules/api_worker"
#   name   = "${var.environment}-lambdaGETReadproduct"
# }

# module "api_worker_read" {
#   source = "./modules/api_worker"
#   name   = "${var.environment}-lambdaGETReadproduct"
# }

module "api_entrypoint_owner" {
  source      = "./modules/api_entrypoint"
  name        = "${var.environment}-api_entrypoint_owner"
  domain_name = "somedomain-name"
  lambda      = [module.api_worker_read.arn, module.api_worker_create.arn]
}
