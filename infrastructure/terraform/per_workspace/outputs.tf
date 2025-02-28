output "dynamodb_cpm_table_name" {
  value = module.cpmtable.dynamodb_table_name
}

output "workspace" {
  value = terraform.workspace
}

output "workspace_type" {
  value = local.workspace_type
}

output "environment" {
  value = var.environment
}

output "invoke_url" {
  value = module.api_entrypoint.invoke_url
}

output "test_data_bucket" {
  value = "${local.project}--${replace(var.account_name, "_", "-")}--test-data"
}

output "certificate_domain_name" {
  value = "https://${module.domain.domain_cert}"
}

# output "assumed_role" {
#   value = var.assume_role
# }


# output "layers_list" {
#   value = var.layers
# }

# output "layer_arns_object" {
#   value = {
#     for key, instance in module.layers : key => instance.layer_arn
#   }
# }

# output "layer_arns_array" {
#   value = [
#     for instance in module.layers : instance.layer_arn
#   ]
# }

# output "lambda_list" {
#   value = var.lambdas
# }

# output "lambda_arns_object" {
#   value = {
#     for key, instance in module.lambdas : key => instance.lambda_arn
#   }
# }

# output "lambda_arns_array" {
#   value = [
#     for instance in module.lambdas : instance.lambda_arn
#   ]
# }

# output "auth_lambda_arn" {
#   value = module.authoriser.lambda_arn
# }

# output "auth_lambda_role_arn" {
#   value = module.authoriser.lambda_role_arn
# }
