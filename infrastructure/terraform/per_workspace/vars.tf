variable "account_name" {
  type = string
}

variable "assume_account" {
  sensitive = true
}

variable "assume_role" {}

variable "environment" {}

variable "deletion_protection_enabled" {
  type    = bool
  default = false
}
