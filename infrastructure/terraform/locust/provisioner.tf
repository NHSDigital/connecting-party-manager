provider "aws" {
  region = local.region

  default_tags {
    tags = {
      Environment      = var.environment
      Workspace        = "${replace(terraform.workspace, "_", "-")}-locust"
      Project          = local.project
      Name             = "${local.project}--${replace(terraform.workspace, "_", "-")}--locust"
      Owner            = "NHSE"
      ProjectShortName = "CPM"
      ProjectFullname  = "Connecting Party Manager"
      WorkspaceType    = "PERSISTENT"
    }
  }
}
