# module "iam_policy_read" {
#   source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
#   version = "5.30.0"
#
#   name        = "${var.name}--iam-policy-read"
#   path        = "/"
#   description = "Read the ${var.name} table"
#
#   tags = {
#     Name = "${var.name}--iam-policy-read"
#   }
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "kms:Decrypt",
#           "kms:DescribeKey"
#         ]
#         Effect = "Allow"
#         Resource = [
#           module.kms.key_arn
#         ]
#       },
#       {
#         Effect = "Allow"
#         Action = [
#           "dynamodb:Query",
#           "dynamodb:Scan",
#           "dynamodb:GetItem",
#         ],
#         Resource = [
#           "${module.dynamodb_table.dynamodb_table_arn}*"
#         ]
#       }
#     ]
#   })
# }
#
# module "iam_policy_write" {
#   source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
#   version = "5.30.0"
#
#   name        = "${var.name}--iam-policy-write"
#   path        = "/"
#   description = "Write to the ${var.name} table"
#
#   tags = {
#     Name = "${var.name}--iam-policy-write"
#   }
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "kms:Encrypt",
#           "kms:GenerateDataKey"
#         ]
#         Effect = "Allow"
#         Resource = [
#           module.kms.key_arn
#         ]
#       },
#       {
#         Effect = "Allow"
#         Action = [
#           "dynamodb:PutItem",
#           "dynamodb:UpdateItem",
#           "dynamodb:DeleteItem",
#         ],
#         Resource = [
#           "${module.dynamodb_table.dynamodb_table_arn}*"
#         ]
#       }
#     ]
#   })
# }
