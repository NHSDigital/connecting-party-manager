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

resource "aws_secretsmanager_secret" "sds-hscn-endpoint" {
  name = "${terraform.workspace}-sds-hscn-endpoint"
}

resource "aws_secretsmanager_secret" "ldap-host" {
  name = "${terraform.workspace}-ldap-host"
}

resource "aws_secretsmanager_secret" "ldap-changelog-user" {
  name = "${terraform.workspace}-ldap-changelog-user"
}

resource "aws_secretsmanager_secret" "ldap-changelog-password" {
  name = "${terraform.workspace}-ldap-changelog-password"
}

resource "aws_secretsmanager_secret" "notify_slack_webhook_url" {
  name = "${terraform.workspace}-notify-slack-webhook-url"
}

resource "aws_secretsmanager_secret" "apigee-app-client-info" {
  name = "${terraform.workspace}--apigee-app-client-info"
}

resource "aws_secretsmanager_secret" "external-id" {
  name = "${terraform.workspace}-external-id"
}

resource "aws_secretsmanager_secret" "destination_vault_arn" {
  name = "destination_vault_arn"
}

resource "aws_secretsmanager_secret" "destination_account_id" {
  name = "destination_account_id"
}
