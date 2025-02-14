output "vpc_name" {
  value = aws_vpc.main.arn
}
output "vpc_arn" {
  value = aws_vpc.main.arn
}
output "vpc_subnets" {
  value = aws_subnet.main.id
}
output "security_groups" {
  value = aws_security_group.lambda_sg.id
}
# output "dynamodb_table_name" {
#   value = module.dynamodb_table.dynamodb_table_id
# }
#
# output "dynamodb_table_arn" {
#   value = module.dynamodb_table.dynamodb_table_arn
# }
# output "vpc_name" {
#   value = module.vpc.name
# }
# output "vpc_arn" {
#   value = module.vpc.vpc_arn
# }
# output "vpc_subnets" {
#   value = module.vpc.intra_subnets
# }
# output "security_groups" {
#   value = [module.vpc.default_security_group_id]
# }
