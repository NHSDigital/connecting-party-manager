locals {
  region      = "eu-west-2"
  project     = "nhsd-cpm"
  environment = terraform.workspace
  prefix      = "${local.project}--${local.environment}"
}
