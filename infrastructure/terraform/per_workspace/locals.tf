locals {
  region         = "eu-west-2"
  project        = "nhse-cpm"
  current_time   = timestamp()
  workspace_type = contains(terraform.workspace, "dev") || contains(terraform.workspace, "ref") || contains(terraform.workspace, "int") || contains(terraform.workspace, "prod") ? "${var.workspace_type} ${upper(replace(terraform.workspace, "_", "-"))}" : "${var.workspace_type}"
}
