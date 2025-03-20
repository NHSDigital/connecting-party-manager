resource "aws_resourcegroups_group" "resource_group" {
  name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--account-wide-resource-group"
  description = "PERSISTENT ${upper(terraform.workspace)} account-wide resource group."
  tags = {
    Name           = "${local.project}--${replace(terraform.workspace, "_", "-")}--account-wide-resource-group"
    CreatedOn      = var.updated_date
    LastUpdated    = var.updated_date
    ExpirationDate = var.expiration_date
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
      "Values": ["${replace(terraform.workspace, "_", "-")}-account-wide"]
    }
  ]
}
JSON
  }
}

module "billing_alarms" {
  source      = "../modules/billing_alarms"
  project     = local.project
  limit       = var.budget_limit
  environment = terraform.workspace
}
