variable "workspace_prefix" {
  type = string
}

variable "etl_name" {
  type = string
}

variable "trigger_name" {
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

variable "assume_account" {
  type = string
}

variable "allowed_triggers" {
}

variable "table_name" {

}
variable "table_arn" {

}

variable "truststore_bucket" {
  default = ""
}

variable "vpc_subnet_ids" {
  default = null
}

variable "vpc_security_group_ids" {
  default = null
}
