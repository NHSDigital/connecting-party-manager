terraform {
  backend "s3" {
    encrypt              = false
    region               = "eu-west-2"
    bucket               = "nhse-cpm--terraform-state-v1.0.0"
    dynamodb_table       = "nhse-cpm--terraform-state-lock-v1.0.0"
    key                  = "terraform-state-infrastructure"
    workspace_key_prefix = "nhse-cpm"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.26.0"
    }
  }
  # required_version = ">= 1.1.0"
}
