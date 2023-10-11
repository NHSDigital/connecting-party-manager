output "layers_list" {
  value = var.layers
}

output "layer_arns" {
  value = {
    for key, instance in module.layers : key => instance.layer_arn
  }
}
