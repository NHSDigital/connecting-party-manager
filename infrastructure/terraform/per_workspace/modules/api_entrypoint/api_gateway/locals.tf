locals {
  apigateway_lambda_arn_prefix = "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2"
  kms = {
    deletion_window_in_days = 7
  }
  methods = [
    for lambda_alias in setsubtract(var.lambdas, ["authoriser"]) :
    { "method_${lambda_alias}" = "${local.apigateway_lambda_arn_prefix}:${var.assume_account}:function:${var.project}--${replace(terraform.workspace, "_", "-")}--${replace(lambda_alias, "_", "-")}-lambda/invocations" }
  ]
  swagger_file = templatefile("${path.root}/../../swagger/dist/aws/swagger.yaml", merge({
    lambda_invoke_arn   = var.authoriser_metadata.lambda_invoke_arn,
    authoriser_iam_role = var.authoriser_metadata.authoriser_iam_role,
    authoriser_name     = var.authoriser_metadata.authoriser_name,
    },
    local.methods...
  ))
}
