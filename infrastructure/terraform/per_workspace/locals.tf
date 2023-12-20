locals {
  region         = "eu-west-2"
  project        = "nhse-cpm"
  current_time   = timestamp()
  workspace_type = strcontains(terraform.workspace, "dev") || strcontains(terraform.workspace, "ref") || strcontains(terraform.workspace, "int") || strcontains(terraform.workspace, "prod") ? "${var.workspace_type} ${upper(replace(terraform.workspace, "_", "-"))}" : "${var.workspace_type}"
  permission_resource_map = {
    kms      = "*"
    dynamodb = "${module.table.dynamodb_table_arn}"
  }
}
