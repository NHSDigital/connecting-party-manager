locals {
  region       = "eu-west-2"
  project      = "nhse-cpm"
  current_time = timestamp()
  ws_type      = replace(terraform.workspace, "_", "-") == "dev" || replace(terraform.workspace, "_", "-") == "ref" || replace(terraform.workspace, "_", "-") == "int" || replace(terraform.workspace, "_", "-") == "prod" || replace(terraform.workspace, "_", "-") == "dev-sandbox" || replace(terraform.workspace, "_", "-") == "int-sandbox" || replace(terraform.workspace, "_", "-") == "ref-sandbox" ? "${var.workspace_type} ${upper(replace(terraform.workspace, "_", "-"))}" : "${var.workspace_type}"
}
