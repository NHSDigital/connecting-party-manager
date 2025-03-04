variable "account_name" {
  type = string
}

variable "assume_account" {
  sensitive = true
}

variable "assume_role" {}

variable "environment" {}

variable "expiration_date" {
  default = "NEVER"
}

variable "updated_date" {
  default = "NEVER"
}

variable "workspace_type" {
  default = "PERSISTENT"
}

variable "budget_limit" {
  default = "450"
  type    = string
}

# variable "source_terraform_role_arn" {
#   description = "ARN of the terraform role in the source account"
#   type        = string
# }
