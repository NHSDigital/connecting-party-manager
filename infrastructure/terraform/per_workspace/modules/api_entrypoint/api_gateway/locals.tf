locals {
  apigateway_lambda_arn_prefix = "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2"
  kms = {
    deletion_window_in_days = 7
  }
}
