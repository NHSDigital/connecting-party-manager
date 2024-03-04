module "api_gateway" {
  source              = "./api_gateway"
  name                = var.name
  lambdas             = var.lambdas
  assume_account      = var.assume_account
  project             = var.project
  authoriser_metadata = var.authoriser_metadata
  domain              = var.domain
}
