module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = "${var.workspace_prefix}--${var.etl_name}--${var.etl_stage}"
  description   = "${replace(var.workspace_prefix, "_", "-")} ${var.etl_name} (${var.etl_stage}) lambda function"
  handler       = "etl.sds.worker.${var.etl_stage}.${var.etl_stage}.handler"
  runtime       = var.python_version
  timeout       = 600
  memory_size   = 10240

  timeouts = {
    create = "5m"
    update = "5m"
    delete = "5m"
  }

  create_current_version_allowed_triggers = false
  allowed_triggers = {
    "${replace(var.workspace_prefix, "_", "-")}--AllowExecutionFromStepFunction--${var.etl_name}--${var.etl_stage}" = {
      service    = "states"
      source_arn = "arn:aws:states:eu-west-2:${var.assume_account}:stateMachine:${var.workspace_prefix}--${var.etl_name}"
    }
  }
  environment_variables = merge(var.environment_variables, { ETL_BUCKET = var.etl_bucket_name })


  create_package         = false
  local_existing_package = "${path.root}/../../../src/etl/sds/worker/${var.etl_stage}/dist/${var.etl_stage}.zip"

  tags = {
    Name = "${var.workspace_prefix}--${var.etl_name}--${var.etl_stage}"
  }

  layers = var.layers

  trusted_entities = [
    {
      type = "Service",
      identifiers = [
        "states.amazonaws.com"
      ]
    }
  ]

  attach_policy_json = true
  policy_json        = var.policy_json
}
