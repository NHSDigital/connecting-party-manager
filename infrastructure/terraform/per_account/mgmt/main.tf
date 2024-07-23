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

module "route53" {
  source    = "./modules/route53"
  workspace = terraform.workspace
}

module "locust_vpc" {
  source      = "./modules/locust-vpc"
  environment = terraform.workspace
  prefix      = "${local.project}--${replace(terraform.workspace, "_", "-")}"
}
