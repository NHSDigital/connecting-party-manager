output "state_machine_arn" {
  value = aws_sfn_state_machine.state_machine.arn
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

output "etl_state_lock_key" {
  value = var.etl_state_lock_key
}

output "proxy_executer" {
  value = module.proxy_lambda_executor
}
