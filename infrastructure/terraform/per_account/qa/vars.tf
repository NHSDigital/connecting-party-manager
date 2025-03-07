variable "account_name" {
  type = string
}

variable "assume_account" {
  sensitive = true
}

variable "assume_role" {}

variable "external_id" {}

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
  default = "475"
  type    = string
}
