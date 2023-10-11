resource "aws_resourcegroups_group" "resource_group" {
  name = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
  tags = {
    Name      = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
    CreatedOn = local.current_time
  }

  lifecycle {
    ignore_changes = [tags["CreatedOn"]]
  }

  resource_query {
    query = <<JSON
{
  "ResourceTypeFilters": ["AWS::AllSupported"],
  "TagFilters": [
    {
      "Key": "Workspace",
      "Values": ["${replace(terraform.workspace, "_", "-")}"]
    }
  ]
}
JSON
  }
}

module "products_table" {
  source      = "./modules/api_storage"
  name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--products-table"
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

module "layers" {
  for_each   = toset(var.layers)
  source     = "./modules/api_worker/api_layer"
  name       = each.key
  layer_name = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda-layer"
}

module "lambdas" {
  for_each    = toset(var.lambdas)
  source      = "./modules/api_worker/api_lambda"
  name        = each.key
  lambda_name = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda"
}


# module "api_worker_create" {
#   source = "./modules/api_worker"
#   name   = "${local.project}--${replace(terraform.workspace, "_", "-")}--lambdaGETReadproduct"
# }

# module "api_worker_createProduct" {
#   source      = "./modules/api_worker"
#   name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--lambdacreateProduct"
#   lambda_name = "createProduct"
# }

# module "api_entrypoint_owner" {
#   source      = "./modules/api_entrypoint"
#   name        = "${local.project}--${replace(terraform.workspace, "_", "-")}-api_entrypoint_owner"
#   domain_name = "somedomain-name"
#   lambda      = [module.api_worker_read.arn, module.api_worker_create.arn]
# }
