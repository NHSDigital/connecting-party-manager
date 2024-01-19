output "state_machine_arn" {
  value = module.step_function.state_machine_arn
}

output "bucket" {
  value = module.bucket.s3_bucket_id
}

output "changelog_key" {
  value = var.changelog_key
}
