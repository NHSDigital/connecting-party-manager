provider "aws" {
  region = local.region

  assume_role {
    role_arn = "arn:aws:iam::${var.assume_account}:role/${var.assume_role}"
  }

  default_tags {
    tags = {
      Environment      = var.environment
      LastUpdated      = var.updated_date
      Workspace        = replace(terraform.workspace, "_", "-")
      Project          = local.project
      Name             = "${local.project}--${replace(terraform.workspace, "_", "-")}"
      Owner            = "NHSE"
      ProjectShortName = "CPM"
      ProjectFullname  = "Connecting Party Manager"
      ExpirationDate   = var.expiration_date
    }
  }
}
