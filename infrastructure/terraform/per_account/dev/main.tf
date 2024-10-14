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

module "bucket_access_logs" {
  source                                = "terraform-aws-modules/s3-bucket/aws"
  version                               = "3.15.2"
  bucket                                = "${local.project}--${replace(terraform.workspace, "_", "-")}--s3-access-logs"
  attach_deny_insecure_transport_policy = true
  attach_access_log_delivery_policy     = true
  force_destroy                         = true
  versioning = {
    enabled = true
  }
  tags = {
    Name = "${local.project}--${replace(terraform.workspace, "_", "-")}--s3-access-logs"
  }
}

module "bucket" {
  source                                = "terraform-aws-modules/s3-bucket/aws"
  version                               = "3.15.2"
  bucket                                = "${local.project}--${replace(terraform.workspace, "_", "-")}--test-data"
  attach_deny_insecure_transport_policy = true
  force_destroy                         = true
  versioning = {
    enabled = true
  }
  tags = {
    Name = "${local.project}--${replace(terraform.workspace, "_", "-")}--test-data"
  }
}

module "truststore_bucket" {
  source                                = "terraform-aws-modules/s3-bucket/aws"
  version                               = "3.15.2"
  bucket                                = "${local.project}--${replace(terraform.workspace, "_", "-")}--truststore"
  attach_deny_insecure_transport_policy = true
  attach_access_log_delivery_policy     = true
  force_destroy                         = true
  versioning = {
    enabled = true
  }
  tags = {
    Name = "${local.project}--${replace(terraform.workspace, "_", "-")}--truststore"
  }
}

resource "aws_s3_bucket_logging" "truststore_to_access_logs" {
  bucket = module.truststore_bucket.s3_bucket_id

  target_bucket = module.bucket_access_logs.s3_bucket_id
  target_prefix = "truststore/log/"
}

module "sds_etl_hscn_vpc" {
  source      = "../modules/sds_etl_hscn_vpc"
  environment = terraform.workspace
  prefix      = local.project
}

module "vpc" {
  source      = "../modules/vpc"
  environment = terraform.workspace
  prefix      = local.project
}


# -------- ROUTE 53 ---------

resource "aws_route53_zone" "dev-ns" {
  name = "api.cpm.dev.national.nhs.uk"
}

module "billing-alert" {
  source                              = "../modules/billing-alert"
  prefix                              = "${local.project}--${terraform.workspace}"
  metric_name                         = "EstimatedCharges"
  metric_statistic                    = "Maximum"
  metric_number_of_evaluation_periods = 1
  threshold_dollars                   = 20
  recipients                          = [] # get from secrets
  tags = {
    Name = "${local.project}--${replace(terraform.workspace, "_", "-")}"
  }
}
