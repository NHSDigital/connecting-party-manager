resource "aws_backup_restore_testing_plan" "backup_restore_testing_plan" {
  name                = "backup_restore_testing_plan"
  schedule_expression = var.restore_testing_plan_scheduled_expression
  start_window_hours  = var.restore_testing_plan_start_window
  recovery_point_selection {
    algorithm             = var.restore_testing_plan_algorithm
    include_vaults        = [aws_backup_vault.main.arn]
    recovery_point_types  = var.restore_testing_plan_recovery_point_types
    selection_window_days = var.restore_testing_plan_selection_window_days
  }

}


resource "aws_backup_restore_testing_selection" "backup_restore_testing_selection_dynamodb" {
  name                      = "backup_restore_testing_selection_dynamodb"
  restore_testing_plan_name = aws_backup_restore_testing_plan.backup_restore_testing_plan.name
  protected_resource_type   = "DynamoDB"
  iam_role_arn              = aws_iam_role.backup.arn

  protected_resource_conditions {
    string_equals {
      key   = "aws:ResourceTag/${var.backup_plan_config_dynamodb.selection_tag}"
      value = "True"
    }
  }
}
