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
variable "bulk_load_chunksize" {
  default = 1000
}
variable "bulk_transform_chunksize" {
  default = 50000
}

variable "etl_state_lock_key" {
  default = "ETL_STATE_LOCK"
}
variable "table_name" {}
variable "table_arn" {}
variable "is_persistent" {}
variable "truststore_bucket" {}
variable "etl_snapshot_bucket" {}
variable "environment" {

}
variable "changenumber_batch" {
  default = 5000
}
