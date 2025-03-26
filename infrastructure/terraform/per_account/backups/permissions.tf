// Allows the role that terraform assumes to create the KMS key that the backup vault will use
resource "aws_iam_policy" "create_kms_keys_policy" {
  name = "${local.project}-create-kms-keys-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:ListKeys",
          "kms:DescribeKey",
          "kms:CreateKey",
          "kms:TagResource",
          "kms:CreateGrant",
          "kms:RetireGrant",
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:Encrypt",
          "kms:ReEncrypt*"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_terraform_create_kms_keys_policy_attachment" {
  policy_arn = aws_iam_policy.create_kms_keys_policy.arn
  role       = var.assume_role
}

// This policy allows the role that terraform assumes to manage backup vaults
resource "aws_iam_policy" "create_backup_vaults_policy" {
  name = "${local.project}-create-backup-vaults-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "backup:ListBackupVaults",
          "backup:DescribeBackupVault",
          "backup:CreateBackupVault",
          "backup:DeleteBackupVault",
          "backup:TagResource",
          "backup:ListTags",
          "backup:PutBackupVaultAccessPolicy",
          "backup:GetBackupVaultAccessPolicy"
        ]
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
        Effect = "Allow"
        Action = [
          "iam:ListRoles",
          "iam:CreateServiceLinkedRole"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_terraform_create_backup_vaults_policy_attachment" {
  policy_arn = aws_iam_policy.create_backup_vaults_policy.arn
  role       = var.assume_role
}
