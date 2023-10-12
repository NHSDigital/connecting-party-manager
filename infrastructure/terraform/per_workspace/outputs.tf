output "layers_list" {
  value = var.layers
}

output "layer_arns_object" {
  value = {
    for key, instance in module.layers : key => instance.layer_arn
  }
}

output "layer_arns_array" {
  value = [
    for instance in module.layers : instance.layer_arn
  ]
}

output "lambda_list" {
  value = var.lambdas
}

output "lambda_arns_object" {
  value = {
    for key, instance in module.lambdas : key => instance.lambda_arn
  }
}

output "lambda_arns_array" {
  value = [
    for instance in module.lambdas : instance.lambda_arn
  ]
}
