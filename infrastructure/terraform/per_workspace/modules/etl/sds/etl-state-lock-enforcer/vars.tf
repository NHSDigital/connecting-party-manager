
variable "workspace_prefix" {
  type = string
}

variable "etl_name" {
  type = string
}

variable "executor_name" {
  type = string
}

variable "python_version" {
  type = string
}

variable "state_machine_arn" {
  type = string
}

variable "notify_lambda_arn" {
  type = string
}

variable "etl_bucket_arn" {
  type = string
}

variable "etl_layer_arn" {
  type = string
}

variable "event_layer_arn" {
  type = string
}

variable "third_party_layer_arn" {
  type = string
}

variable "sds_layer_arn" {
  type = string
}

variable "allowed_triggers" {
}

variable "extra_policies" {
  default = []
}

variable "environment_variables" {
}
