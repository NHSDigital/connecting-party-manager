variable "name" {}

variable "python_version" {
  default = "python3.11"
}

variable "lambda_name" {
  default = ""
}

variable "layers" {
  type = list(string)
}

variable "source_path" {}

variable "attach_policy_json" {
  default = false
}

variable "policy_json" {
  default = ""
}

variable "trusted_entities" {
  default = []
}

variable "allowed_triggers" {
  default = {}
}

variable "environment_variables" {
  default = {}
}

variable "attach_policy_statements" {
  default = false
}

variable "policy_statements" {
  default = {}
}
