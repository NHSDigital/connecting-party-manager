variable "workspace_prefix" {
  type = string
}

variable "etl_name" {
  type = string
}

variable "etl_stage" {
  type = string
}

variable "python_version" {
  type = string
}

variable "etl_bucket_name" {
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
