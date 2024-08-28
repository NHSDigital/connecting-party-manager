
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

variable "domain_layer_arn" {
  type = string
}

variable "sds_layer_arn" {
  type = string
}


variable "allowed_triggers" {
}

variable "table_arn" {

}

variable "vpc_subnet_ids" {
  default = null
}

variable "vpc_security_group_ids" {
  default = null
}
variable "extra_policies" {
  default = []
}

variable "environment_variables" {
}

variable "sqs_queue_arn" {

}
