variable "name" {}

variable "environment" {}

variable "range_key" {}

variable "hash_key" {}

variable "deletion_protection_enabled" {
  type    = bool
  default = false
}

variable "kms_deletion_window_in_days" {
  type    = number
  default = 7
}

variable "attributes" {
  type = list(object(
    {
      name = string
      type = string
    }
  ))
  default = []
}

variable "global_secondary_indexes" {
  type = list(object(
    {
      name            = string
      hash_key        = string
      range_key       = string
      projection_type = string
    }
  ))
  default = []
}
