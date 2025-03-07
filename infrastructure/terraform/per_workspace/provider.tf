provider "aws" {
  region = local.region

  assume_role {
    role_arn    = "arn:aws:iam::${var.assume_account}:role/${var.assume_role}"
    external_id = var.external_id
  }

  default_tags {
    tags = {
      Environment      = var.environment
      Workspace        = replace(terraform.workspace, "_", "-")
      Project          = local.project
      Name             = "${local.project}--${replace(terraform.workspace, "_", "-")}"
      Owner            = "NHSE"
      ProjectShortName = "CPM"
      ProjectFullname  = "Connecting Party Manager"
      WorkspaceType    = var.workspace_type
    }
  }
}
