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

output "event_rule_arn" {
  value = module.schedule_trigger_update.arn
}

output "update_lambda_arn" {
  value = module.trigger_update.lambda_function.lambda_function_arn
}
