output "workspace" {
  value = terraform.workspace
}

output "workspace_type" {
  value = local.workspace_type
}

output "environment" {
  value = var.environment
}
