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

# -------- ROUTE 53 ---------

resource "aws_route53_zone" "dev-ns" {
  name = "api.cpm.dev.national.nhs.uk"
}

module "layers" {
  for_each       = toset(var.layers)
  source         = "../../modules/api_worker/api_layer"
  name           = each.key
  python_version = var.python_version
  layer_name     = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}"
  source_path    = "${path.module}/../../../../src/layers/${each.key}/dist/${each.key}.zip"
}

module "third_party_layers" {
  for_each       = toset(var.third_party_layers)
  source         = "../../modules/api_worker/api_layer"
  name           = each.key
  python_version = var.python_version
  layer_name     = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}"
  source_path    = "${path.module}/../../../../src/layers/third_party/dist/${each.key}.zip"
}
