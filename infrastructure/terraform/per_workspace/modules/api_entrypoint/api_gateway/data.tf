data "template_file" "swagger" {
  template = sensitive(file("${path.root}/../../swagger/dist/aws/swagger.yaml"))
  vars = merge(
    { environment = terraform.workspace },
    var.authoriser_metadata,
    {
      for lambda_alias in setsubtract(var.lambdas, ["authoriser"]) :
      "method_${lambda_alias}" => "${local.apigateway_lambda_arn_prefix}:${var.assume_account}:function:${var.project}--${replace(terraform.workspace, "_", "-")}--${replace(lambda_alias, "_", "-")}-lambda/invocations"
    }
  )
}
