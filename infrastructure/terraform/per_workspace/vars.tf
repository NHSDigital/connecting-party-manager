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

variable "expiration_date" {
  default = "NEVER"
}

variable "updated_date" {
  default = "NEVER"
}

variable "layers_directory" {
  default = "../src/layers"
}

variable "layers" {
  type = list(string)
}

variable "lambdas" {
  type = list(string)
}
