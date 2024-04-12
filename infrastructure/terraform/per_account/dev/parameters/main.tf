resource "aws_resourcegroups_group" "resource_group" {
  name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--parameter-resource-group"
  description = "${var.workspace_type} ${upper(terraform.workspace)} parameter resource group."
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

resource "aws_secretsmanager_secret" "apigee-credentials" {
  name = "${terraform.workspace}-apigee-credentials"
}

resource "aws_secretsmanager_secret" "apigee-cpm-apikey" {
  name = "${terraform.workspace}-apigee-cpm-apikey"
}

resource "aws_secretsmanager_secret" "apigee-app-key" {
  name = "${terraform.workspace}-apigee-app-key"
}
resource "aws_secretsmanager_secret" "sds-ldap-endpoint" {
  name = "${terraform.workspace}-sds-ldap-endpoint"
}

resource "aws_secretsmanager_secret" "ldap-host" {
  name = "${terraform.workspace}-ldap-host"
}
