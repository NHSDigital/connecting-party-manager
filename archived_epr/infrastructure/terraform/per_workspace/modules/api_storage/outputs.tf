output "dynamodb_table_name" {
  value = module.dynamodb_table.dynamodb_table_id
}

output "dynamodb_table_arn" {
  value = module.dynamodb_table.dynamodb_table_arn
}
