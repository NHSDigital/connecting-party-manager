provider "aws" {
  region = local.region

  assume_role {
    role_arn = "arn:aws:iam::${var.assume_account}:role/${var.assume_role}"
  }

  default_tags {
    tags = {
      Environment      = var.environment
      Workspace        = "${replace(terraform.workspace, "_", "-")}-dns"
      Project          = local.project
      Name             = "${local.project}--${replace(terraform.workspace, "_", "-")}--dns"
      Owner            = "NHSE"
      ProjectShortName = "CPM"
      ProjectFullname  = "Connecting Party Manager"
      WorkspaceType    = "PERSISTENT"
    }
  }
}
