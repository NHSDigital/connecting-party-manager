resource "aws_resourcegroups_group" "resource_group" {
  name = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
  tags = {
    Name      = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
    CreatedOn = var.updated_date
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
  for_each    = toset(var.layers)
  source      = "./modules/api_worker/api_layer"
  name        = each.key
  layer_name  = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda-layer"
  source_path = "${path.module}/../../../src/layers/${each.key}/dist/${each.key}.zip"
}

# module "lambdas" {
#   for_each    = toset(var.lambdas)
#   source      = "./modules/api_worker/api_lambda"
#   name        = each.key
#   lambda_name = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda"
#   layers      = [for instance in module.layers : instance.layer_arn]
#   source_path = "${path.module}/../../../src/api/${each.key}/dist/${each.key}.zip"
# }
