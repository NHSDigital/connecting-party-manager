terraform {
  backend "s3" {
    encrypt              = false
    region               = "eu-west-2"
    bucket               = "nhse-cpm--terraform-state-v1.0.0"
    dynamodb_table       = "nhse-cpm--terraform-state-lock-v1.0.0"
    key                  = "terraform-state-infrastructure-dev-account-wide"
    workspace_key_prefix = "nhse-cpm"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.91.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
    external = {
      source  = "hashicorp/external"
      version = "~> 2.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}
