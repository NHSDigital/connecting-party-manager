# this backup plan shouldn't include a continous backup rule as it isn't supported for DynamoDB
resource "aws_backup_plan" "dynamodb" {
  name = "${local.resource_name_prefix}-dynamodb-plan"

  dynamic "rule" {
    for_each = var.backup_plan_config_dynamodb.rules
    content {
      recovery_point_tags = {
        backup_rule_name = rule.value.name
      }
      rule_name         = rule.value.name
      target_vault_name = aws_backup_vault.main.name
      schedule          = rule.value.schedule
      lifecycle {
        delete_after       = rule.value.lifecycle.delete_after != null ? rule.value.lifecycle.delete_after : null
        cold_storage_after = rule.value.lifecycle.cold_storage_after != null ? rule.value.lifecycle.cold_storage_after : null
      }
      dynamic "copy_action" {
        for_each = var.backup_copy_vault_arn != "" && var.backup_copy_vault_account_id != "" && rule.value.copy_action != null ? rule.value.copy_action : {}
        content {
          lifecycle {
            delete_after = copy_action.value
          }
          destination_vault_arn = var.backup_copy_vault_arn
        }
      }
    }
  }
}

resource "aws_backup_selection" "dynamodb" {
  iam_role_arn = aws_iam_role.backup.arn
  name         = "${local.resource_name_prefix}-dynamodb-selection"
  plan_id      = aws_backup_plan.dynamodb.id

  selection_tag {
    key   = var.backup_plan_config_dynamodb.selection_tag
    type  = "STRINGEQUALS"
    value = "True"
  }
}
