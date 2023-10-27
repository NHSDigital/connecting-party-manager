resource "aws_resourcegroups_group" "resource_group" {
  name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--resource-group"
  description = "${var.workspace_type} workspace resource group."
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

module "products_table" {
  source      = "./modules/api_storage"
  name        = "${local.project}--${replace(terraform.workspace, "_", "-")}--products-table"
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
}

module "layers" {
  for_each    = toset(var.layers)
  source      = "./modules/api_worker/api_layer"
  name        = each.key
  layer_name  = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda-layer"
  source_path = "${path.module}/../../../src/layers/${each.key}/dist/${each.key}.zip"
}

module "lambdas" {
  for_each    = setsubtract(var.lambdas, ["authoriser"])
  source      = "./modules/api_worker/lambda"
  name        = each.key
  lambda_name = "${local.project}--${replace(terraform.workspace, "_", "-")}--${replace(each.key, "_", "-")}-lambda"
  layers      = [for instance in module.layers : instance.layer_arn]
  source_path = "${path.module}/../../../src/api/${each.key}/dist/${each.key}.zip"
  #apigateway_execution_arn = module.api_entrypoint.execution_arn
}

module "authoriser" {
  name        = "authoriser"
  source      = "./modules/api_worker/lambda"
  lambda_name = "${local.project}--${replace(terraform.workspace, "_", "-")}--authoriser-lambda"
  source_path = "${path.module}/../../../src/api/authoriser/dist/authoriser.zip"
  layers      = [for instance in module.layers : instance.layer_arn]
  assume_role_policy_statements = {
    authoriser = {
      effect  = "Allow",
      actions = ["sts:AssumeRole"],
      principals = {
        account_principal = {
          type        = "AWS",
          identifiers = ["apigateway.amazonaws.com"]
        }
      }
    }
  }
  attach_policy_statements = true
  policy_statements = {
    lambdaInvoke = {
      effect    = "Allow",
      actions   = ["lambda:InvokeFunction"]
      resources = ["module.authoriser.lambda_arn"]
    }
  }
}

module "kms__cloudwatch" {
  source         = "./modules/kms"
  name           = "${local.project}--${replace(terraform.workspace, "_", "-")}--cloudwatch"
  assume_account = var.assume_account
  prefix         = local.project
}



# module "api_entrypoint" {
#   source         = "./modules/api_entrypoint"
#   assume_account = var.assume_account
#   project        = local.project

#   name                = "${local.project}--${replace(terraform.workspace, "_", "-")}--api-entrypoint"
#   kms_key_id          = module.kms__cloudwatch.kms_arn
#   lambdas             = setsubtract(var.lambdas, ["authoriser"])
#   authoriser_metadata = module.authoriser.metadata
# }
