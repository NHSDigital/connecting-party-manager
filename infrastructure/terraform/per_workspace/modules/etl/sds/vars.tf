variable "workspace_prefix" {}
variable "assume_account" {}
variable "python_version" {}
variable "event_layer_arn" {}
variable "third_party_layer_arn" {}
variable "changelog_key" {
  default = "changelog-number"
}
variable "table_arn" {}
variable "table_name" {}
