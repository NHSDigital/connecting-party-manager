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


resource "aws_secretsmanager_secret" "source-account-id-for-backup-prod" {
  name        = "${terraform.workspace}-source-account-id-prod"
  description = "ID of the account we want to backup"
}

resource "aws_secretsmanager_secret" "source-account-id-for-backup-dev" {
  name        = "${terraform.workspace}-source-account-id-dev"
  description = "ID of the account we want to backup"
}

resource "aws_secretsmanager_secret" "external-id" {
  name = "${terraform.workspace}-external-id"
}
