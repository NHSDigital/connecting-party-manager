variable "workspace_prefix" {}
variable "assume_account" {}
variable "python_version" {}
variable "event_layer_arn" {}
variable "third_party_core_layer_arn" {}
variable "third_party_sds_update_layer_arn" {}
variable "sds_layer_arn" {}
variable "domain_layer" {}
variable "changelog_key" {
  default = "changelog-number"
}
variable "table_name" {}
variable "table_arn" {}
variable "is_persistent" {}
variable "truststore_bucket" {}
variable "environment" {

}
