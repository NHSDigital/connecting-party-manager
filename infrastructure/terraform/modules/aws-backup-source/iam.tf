data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["backup.amazonaws.com", "cloudformation.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "backup" {
  name               = "${var.project_name}BackupRole"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "backup" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
  role       = aws_iam_role.backup.name
}

resource "aws_iam_role_policy_attachment" "restore" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
  role       = aws_iam_role.backup.name
}


# resource "aws_iam_role_policy_attachment" "backup_full_access" {
#   policy_arn = "arn:aws:iam::aws:policy/AWSBackupFullAccess"
#   role       = aws_iam_role.backup.name
# }


# resource "aws_iam_policy" "restore_testing_selection_permissions" {
#   name = "${local.resource_name_prefix}-source-account-backup-permissions"
#   policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Effect = "Allow",
#         Action = [
#           "backup:*",
#           "cloudformation:*"
#         ],
#         Resource = "*"
#       },
#     ]
#   })
# }

# resource "aws_iam_role_policy_attachment" "source_account_backup_permissions" {
#   policy_arn = aws_iam_policy.restore_testing_selection_permissions.arn
#   role       = aws_iam_role.backup.name
# }
