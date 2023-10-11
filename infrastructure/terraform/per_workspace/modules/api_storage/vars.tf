variable "name" {}

variable "environment" {}

variable "hash_key" {}

variable "range_key" {}

variable "attributes" {
  type = list(object(
    {
      name = string
      type = string
    }
  ))
}

variable "deletion_protection_enabled" {
  type = bool
}

variable "kms_deletion_window_in_days" {}
