locals {
  region         = "eu-west-2"
  project        = "nhse-cpm"
  current_time   = timestamp()
  workspace_type = var.workspace_type
  permission_resource_map = {
    kms      = "*"
    dynamodb = "${module.table.dynamodb_table_arn}"
  }
  # e.g. api.cpm.dev.national.nhs.uk
  zone = var.domain

  domain = "${terraform.workspace}.${var.domain}"
}
