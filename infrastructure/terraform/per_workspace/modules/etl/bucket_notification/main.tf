resource "aws_s3_bucket_notification" "notification" {
  bucket = var.source_bucket.s3_bucket_id

  lambda_function {
    lambda_function_arn = var.target_lambda.lambda_function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.filter_prefix
    filter_suffix       = var.filter_suffix
  }
}

resource "aws_lambda_permission" "s3_bucket_can_invoke_lambda" {
  statement_id  = "${var.target_lambda.lambda_function_name}--${var.source_bucket.s3_bucket_id}--AllowExecution"
  action        = "lambda:InvokeFunction"
  function_name = var.target_lambda.lambda_function_arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.source_bucket.s3_bucket_arn
}
