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

variable "third_party_layers" {
  type = list(string)
}

variable "api_lambda_layers" {
  type = list(string)
  default = [
    "domain",
    "event",
    "api_utils"
  ]
}

variable "lambdas" {
  type = list(string)
}

variable "workspace_type" {
  type    = string
  default = "PERSISTENT"
}

variable "apigateway_arn_prefix" {
  type    = string
  default = "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2"
}

variable "python_version" {
  default = "python3.12"
}

variable "domain" {
  type = string
}
