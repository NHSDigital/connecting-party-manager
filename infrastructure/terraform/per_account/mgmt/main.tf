resource "aws_resourcegroups_group" "resource_group" {
  name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--dns-resource-group"
  description = "PERSISTENT ${upper(terraform.workspace)} DNS resource group."
  tags = {
    Name           = "${local.project}--${replace(terraform.workspace, "_", "-")}--dns-resource-group"
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
      "Values": ["${replace(terraform.workspace, "_", "-")}-dns"]
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

module "route53" {
  source    = "./modules/route53"
  workspace = terraform.workspace
}

module "locust_vpc" {
  source      = "./modules/locust-vpc"
  environment = terraform.workspace
  prefix      = "${local.project}--${replace(terraform.workspace, "_", "-")}"
}
