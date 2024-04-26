output "state_machine_arn" {
  value = module.step_function.state_machine_arn
}

output "bucket" {
  value = module.bucket.s3_bucket_id
}

output "changelog_key" {
  value = var.changelog_key
}

output "bulk_trigger_prefix" {
  value = local.bulk_trigger_prefix
}

output "notify_lambda_arn" {
  value = module.notify.arn
}
