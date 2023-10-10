provider "aws" {
  access_key = "mock_access_key"
  secret_key = "mock_secret_key"
  region     = "us-east-1"

  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    apigateway     = "http://localhost:4566"
    apigatewayv2   = "http://localhost:4566"
    cloudformation = "http://localhost:4566"
    cloudwatch     = "http://localhost:4566"
    dynamodb       = "http://localhost:4566"
    ec2            = "http://localhost:4566"
    es             = "http://localhost:4566"
    elasticache    = "http://localhost:4566"
    firehose       = "http://localhost:4566"
    iam            = "http://localhost:4566"
    kinesis        = "http://localhost:4566"
    lambda         = "http://localhost:4566"
    rds            = "http://localhost:4566"
    redshift       = "http://localhost:4566"
    route53        = "http://localhost:4566"
    s3             = "http://s3.localhost.localstack.cloud:4566"
    secretsmanager = "http://localhost:4566"
    ses            = "http://localhost:4566"
    sns            = "http://localhost:4566"
    sqs            = "http://localhost:4566"
    ssm            = "http://localhost:4566"
    stepfunctions  = "http://localhost:4566"
    sts            = "http://localhost:4566"
  }

  default_tags {
    tags = {
      Environment      = var.environment
      Created          = local.created
      Workspace        = replace(terraform.workspace, "_", "-")
      Project          = local.project
      Name             = "${local.project}--${replace(terraform.workspace, "_", "-")}"
      Owner            = "NHSE"
      ProjectShortName = "CPM"
      ProjectFullname  = "Connecting Party Manager"
    }
  }
}

resource "aws_resourcegroups_group" "resource_group" {
  name = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
  tags = {
    Name    = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
    Created = local.created
  }

  resource_query {
    query = <<JSON
{
  "ResourceTypeFilters": ["AWS::AllSupported"],
  "TagFilters": [
    {
      "Key": "Workspace",
      "Values": ["${replace(terraform.workspace, "_", "-")}"]
    }
  ]
}
JSON
  }
}

module "products_table" {
  source = "../terraform/per_workspace/modules/api_storage"

  name        = "${var.environment}-products-table"
  environment = var.environment
  hash_key    = "pk"
  range_key   = "sk"
  attributes = [
    {
      name = "pk"
      type = "S"
    },
    {
      name = "sk"
      type = "S"
    }
  ]
  deletion_protection_enabled = var.deletion_protection_enabled
  kms_deletion_window_in_days = 7
  created                     = local.created
}
