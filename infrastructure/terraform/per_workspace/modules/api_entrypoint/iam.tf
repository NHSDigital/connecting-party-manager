# resource "aws_iam_role_policy" "invoke_function" {
#   name = "default"
#   role = var.lambda_authoriser_id

#   policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Action   = "lambda:InvokeFunction",
#         Effect   = "Allow",
#         Resource = var.lambda_authoriser_arn
#       }
#     ]
#   })
# }
