resource "aws_resourcegroups_group" "resource_group" {
  name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--parameter-resource-group"
  description = "${var.workspace_type} parameter resource group."
  tags = {
    Name           = "${local.project}--${replace(terraform.workspace, "_", "-")}--parameter-resource-group"
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
      "Values": ["${replace(terraform.workspace, "_", "-")}-parameters"]
    }
  ]
}
JSON
  }
}

resource "aws_secretsmanager_secret" "dev-apigee-credentials" {
  name = "${terraform.workspace}-apigee-credentials"
}
