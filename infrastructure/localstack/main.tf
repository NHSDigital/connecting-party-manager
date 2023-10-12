resource "aws_resourcegroups_group" "resource_group" {
  name = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
  tags = {
    Name    = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
    Created = local.created
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
  source = "../terraform/per_workspace/modules/api_storage"

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
  created                     = local.created
}
