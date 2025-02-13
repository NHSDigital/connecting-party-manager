locals {
  region         = "eu-west-2"
  project        = "nhse-cpm-epr"
  current_time   = timestamp()
  workspace_type = var.workspace_type
  permission_resource_map = {
    kms = ["*"]
  }
  # e.g. api.cpm.dev.national.nhs.uk
  zone   = var.domain
  domain = "${terraform.workspace}.${var.domain}"
}
