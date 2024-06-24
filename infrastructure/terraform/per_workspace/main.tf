resource "aws_resourcegroups_group" "resource_group" {
  name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
  description = "${local.workspace_type} workspace resource group."
  tags = {
    Name           = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
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
      "Values": ["${replace(terraform.workspace, "_", "-")}"]
    }
  ]
}
JSON
  }
}

data "aws_secretsmanager_secret" "cpm_apigee_api_key" {
  name = "${var.environment}-apigee-cpm-apikey"
}

module "table" {
  source                      = "./modules/api_storage"
  name                        = "${local.project}--${replace(terraform.workspace, "_", "-")}--table"
  environment                 = var.environment
  deletion_protection_enabled = var.deletion_protection_enabled
  kms_deletion_window_in_days = 7
  range_key                   = "sk"
  hash_key                    = "pk"

  attributes = [
    { name = "pk", type = "S" },
    { name = "sk", type = "S" },
    { name = "pk_1", type = "S" },
    { name = "sk_1", type = "S" },
    { name = "pk_2", type = "S" },
    { name = "sk_2", type = "S" }
  ]

  global_secondary_indexes = [
    {
      name            = "idx_gsi_1"
      hash_key        = "pk_1"
      range_key       = "sk_1"
      projection_type = "ALL"
    },
    {
      name            = "idx_gsi_2"
      hash_key        = "pk_2"
      range_key       = "sk_2"
      projection_type = "ALL"
    }
  ]
}

module "search" {
  source       = "./modules/search"
  name         = "${local.project}--${replace(terraform.workspace, "_", "-")}--os"
  database_arn = module.table.dynamodb_table_arn
  account_id   = var.assume_account
}

module "layers" {
  for_each       = toset(var.layers)
  source         = "./modules/api_worker/api_layer"
  name           = each.key
  python_version = var.python_version
  layer_name     = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda-layer"
  source_path    = "${path.module}/../../../src/layers/${each.key}/dist/${each.key}.zip"
}

module "third_party_layers" {
  for_each       = toset(var.third_party_layers)
  source         = "./modules/api_worker/api_layer"
  name           = each.key
  python_version = var.python_version
  layer_name     = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda-layer"
  source_path    = "${path.module}/../../../src/layers/third_party/dist/${each.key}.zip"
}

module "lambdas" {
  for_each       = setsubtract(var.lambdas, ["authoriser"])
  source         = "./modules/api_worker/api_lambda"
  python_version = var.python_version
  name           = each.key
  lambda_name    = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda"
  //Compact will remove all nulls from the list and create a new one - this is because TF throws an error if there is a null item in the list.
  layers = concat(
    compact([for instance in module.layers : contains(var.api_lambda_layers, instance.name) ? instance.layer_arn : null]),
    [element([for instance in module.third_party_layers : instance if instance.name == "third_party_core"], 0).layer_arn]
  )
  source_path = "${path.module}/../../../src/api/${each.key}/dist/${each.key}.zip"
  allowed_triggers = {
    "AllowExecutionFromAPIGateway-${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}" = {
      service    = "apigateway"
      source_arn = "${module.api_entrypoint.execution_arn}/*/*/*"
    }
  }
  environment_variables = {
    DYNAMODB_TABLE = module.table.dynamodb_table_name
  }
  attach_policy_statements = true
  policy_statements = {
    for file in fileset("${path.module}/../../../src/api/${each.key}/policies", "*.json") : replace(file, ".json", "") => {
      effect    = "Allow"
      actions   = jsondecode(file("${path.module}/../../../src/api/${each.key}/policies/${file}"))
      resources = local.permission_resource_map[replace(file, ".json", "")]
    }
  }
}

module "authoriser" {
  name           = "authoriser"
  source         = "./modules/api_worker/api_lambda"
  python_version = var.python_version
  lambda_name    = "${local.project}--${replace(terraform.workspace, "_", "-")}--authoriser-lambda"
  source_path    = "${path.module}/../../../src/api/authoriser/dist/authoriser.zip"
  environment_variables = {
    ENVIRONMENT = var.environment
  }
  layers = concat(
    compact([for instance in module.layers : contains(var.api_lambda_layers, instance.name) ? instance.layer_arn : null]),
    [element([for instance in module.third_party_layers : instance if instance.name == "third_party_core"], 0).layer_arn]
  )
  trusted_entities = [
    {
      type = "Service",
      identifiers = [
        "apigateway.amazonaws.com"
      ]
    }
  ]

  attach_policy_json = true
  policy_json        = <<-EOT
    {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Action": "lambda:InvokeFunction",
              "Effect": "Allow",
              "Resource": "arn:aws:lambda:eu-west-2:${var.assume_account}:function:${local.project}--${replace(terraform.workspace, "_", "-")}--authoriser-lambda"
          },
          {
              "Action": "secretsmanager:GetSecretValue",
              "Effect": "Allow",
              "Resource": "${data.aws_secretsmanager_secret.cpm_apigee_api_key.arn}"
          }
      ]
    }
  EOT
}

module "domain" {
  source = "./modules/domain"
  domain = local.domain
  zone   = local.zone
}

module "api_entrypoint" {
  source              = "./modules/api_entrypoint"
  assume_account      = var.assume_account
  project             = local.project
  name                = "${local.project}--${replace(terraform.workspace, "_", "-")}--api-entrypoint"
  lambdas             = setsubtract(var.lambdas, ["authoriser"])
  authoriser_metadata = module.authoriser.metadata
  domain              = module.domain.domain_cert
  depends_on          = [module.domain]
}

data "aws_s3_bucket" "truststore_bucket" {
  bucket = "${local.project}--${replace(var.environment, "_", "-")}--truststore"
}


module "sds_etl" {
  source                           = "./modules/etl/sds"
  workspace_prefix                 = "${local.project}--${replace(terraform.workspace, "_", "-")}"
  assume_account                   = var.assume_account
  python_version                   = var.python_version
  event_layer_arn                  = element([for instance in module.layers : instance if instance.name == "event"], 0).layer_arn
  third_party_core_layer_arn       = element([for instance in module.third_party_layers : instance if instance.name == "third_party_sds"], 0).layer_arn
  third_party_sds_update_layer_arn = element([for instance in module.third_party_layers : instance if instance.name == "third_party_sds_update"], 0).layer_arn
  domain_layer                     = element([for instance in module.layers : instance if instance.name == "domain"], 0).layer_arn
  sds_layer_arn                    = element([for instance in module.layers : instance if instance.name == "sds"], 0).layer_arn
  table_name                       = module.table.dynamodb_table_name
  table_arn                        = module.table.dynamodb_table_arn
  is_persistent                    = var.workspace_type == "PERSISTENT"
  truststore_bucket                = data.aws_s3_bucket.truststore_bucket
  environment                      = var.environment
}
