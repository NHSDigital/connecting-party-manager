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

module "iam__api-gateway-to-cloudwatch" {
  source  = "../modules/iam__api-gateway-to-cloudwatch"
  project = local.project
}

module "bucket" {
  source        = "terraform-aws-modules/s3-bucket/aws"
  version       = "3.15.2"
  bucket        = "${local.project}--${replace(terraform.workspace, "_", "-")}--test-data"
  force_destroy = true
  versioning = {
    enabled = true
  }
  tags = {
    Name = "${local.project}--${replace(terraform.workspace, "_", "-")}--test-data"
  }
}

module "truststore_bucket" {
  source        = "terraform-aws-modules/s3-bucket/aws"
  version       = "3.15.2"
  bucket        = "${local.project}--${replace(terraform.workspace, "_", "-")}--truststore"
  force_destroy = true
  versioning = {
    enabled = true
  }
  tags = {
    Name = "${local.project}--${replace(terraform.workspace, "_", "-")}--truststore"
  }
}

module "vpc" {
  source      = "../modules/vpc"
  environment = terraform.workspace
  prefix      = local.project
}

# -------- ROUTE 53 ---------

resource "aws_route53_zone" "prod-ns" {
  name = "api.cpm.national.nhs.uk"
}
