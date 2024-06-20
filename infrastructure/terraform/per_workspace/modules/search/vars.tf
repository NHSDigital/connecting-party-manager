variable "name" {
  type = string
}

variable "database_arn" {
  type = string
}

variable "account_id" {
  type = string
}

variable "kms_deletion_window_in_days" {
  type    = number
  default = 7
}
