variable "name" {}

variable "python_version" {
  default = "python3.11"
}

variable "lambda_name" {}

variable "layers" {
  type = list(string)
}

variable "source_path" {}

variable "assume_role_policy_statements" {
  default = {}
}

variable "attach_policy_statements" {
  default = false
}

variable "policy_statements" {
  default = {}
}
