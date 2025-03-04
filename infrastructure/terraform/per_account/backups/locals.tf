locals {
  region       = "eu-west-2"
  project      = "nhse-cpm"
  current_time = timestamp()
  # source_account_id      = data.aws_arn.source_terraform_role.account
  # destination_account_id = var.assume_account
}
