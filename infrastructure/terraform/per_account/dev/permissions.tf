resource "aws_iam_policy" "source_account_backup_permissions" {
  name = "${local.project}-${var.environment}-source-account-backup-permissions"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "backup:ListBackupPlans",
          "backup:CreateBackupPlan",
          "backup:DeleteBackupPlan",
          "backup:GetBackupPlan",
          "backup:UpdateBackupPlan",
          "backup:GetBackupPlan",
          "backup:CreateReportPlan",
          "backup:DeleteReportPlan",
          "backup:DescribeReportPlan",
          "backup:UpdateReportPlan",
          "backup:ListReportPlans",
          "backup:TagResource",
          "backup:ListTags",
          "backup:CreateFramework",
          "backup:DeleteFramework",
          "backup:DescribeFramework",
          "backup:UpdateFramework",
          "backup:ListFrameworks",
          "backup:CreateBackupVault",
          "backup:DeleteBackupVault",
          "backup:DescribeBackupVault",
          "backup:ListBackupVaults",
          "backup:PutBackupVaultAccessPolicy",
          "backup:GetBackupVaultAccessPolicy",
          "backup:CreateBackupSelection",
          "backup:GetBackupSelection",
          "backup:DeleteBackupSelection",
          "backup:CreateRestoreTestingPlan",
          "backup:DeleteRestoreTestingPlan",
          "backup:GetRestoreTestingPlan",
          "backup:ListRestoreTestingPlans",
          "backup:UpdateRestoreTestingPlan",
          "backup:CreateRestoreTestingSelection",
          "backup:GetRestoreTestingSelection",
          "backup:PutBackupVaultNotifications",
          "backup:GetBackupVaultNotifications",
          "backup:DeleteBackupVaultNotifications"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "backup-storage:*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "kms:ListKeys",
          "kms:DescribeKey",
          "kms:DisableKey",
          "kms:CreateKey",
          "kms:ListAliases",
          "kms:CreateAlias",
          "kms:DeleteAlias",
          "kms:TagResource"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:GetSecretValue"
        ],
        Resource = [
          "arn:aws:secretsmanager:*:${var.assume_account}:secret:destination_vault_arn-*",
          "arn:aws:secretsmanager:*:${var.assume_account}:secret:destination_account_id-*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "iam:UpdateAssumeRolePolicy"
        ],
        Resource = [
          "arn:aws:iam::${var.assume_account}:role/*",
          "arn:aws:iam::${var.assume_account}:policy/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "SNS:SetSubscriptionAttributes"
        ],
        Resource = [
          "arn:aws:sns:*:${var.assume_account}:*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "logs:ListTagsForResource"
        ],
        Resource = [
          "arn:aws:logs:*:${var.assume_account}:log-group:*"
        ]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "source_account_backup_permissions" {
  policy_arn = aws_iam_policy.source_account_backup_permissions.arn
  role       = var.assume_role
}
