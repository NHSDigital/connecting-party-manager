# module "iam_opensearch_pipeline_policy" {
#   source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
#   version = "5.30.0"

#   name        = "${var.name}-pipeline-policy"
#   path        = "/"
#   description = "Policy for the opensearch pipeline"

#   tags = {
#     Name = "${var.name}-pipeline-policy"
#   }

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow",
#         Action = [
#           "dynamodb:*"
#         ],
#         Resource = [
#           "${var.database_arn}",
#           "${var.database_arn}/*"
#         ]
#       },
#       {
#         Effect   = "Allow",
#         Action   = "es:DescribeDomain",
#         Resource = "arn:aws:es:*:${var.account_id}:domain/*"
#       },
#       {
#         Effect   = "Allow",
#         Action   = "es:ESHttp*",
#         Resource = "${data.aws_opensearch_domain.opensearch_domain.arn}/*"
#       },
#       {
#         Effect = "Allow",
#         Action = [
#           "s3:GetObject",
#           "s3:PutObject",
#           "s3:ListBucket"
#         ],
#         Resource = [
#           "${aws_s3_bucket.opensearch_s3_bucket.arn}",
#           "${aws_s3_bucket.opensearch_s3_bucket.arn}/*"
#         ]
#       },
#       {
#         Effect = "Allow",
#         Action = [
#           "kms:Decrypt",
#           "kms:Encrypt",
#           "kms:GenerateDataKey",
#           "kms:DescribeKey"
#         ],
#         Resource = [
#           module.kms.key_arn
#         ]
#       }
#     ]
#   })
# }

data "aws_iam_policy_document" "opensearch_pipeline_policy_document" {
  statement {
    sid = "AllowDatabseAccess"
    actions = [
      "dynamodb:*",
    ]

    resources = [
      "${var.database_arn}",
      "${var.database_arn}/*",
    ]
  }

  statement {
    sid = "AllowDomainAccess"
    actions = [
      "es:DescribeDomain",
    ]

    resources = [
      "arn:aws:es:*:${var.account_id}:domain/*",
    ]
  }

  statement {
    sid = "AllowDashAccess"
    actions = [
      "es:ESHttp*",
    ]

    resources = [
      #"${data.aws_opensearch_domain.opensearch_domain.arn}/*",
      "arn:aws:es:eu-west-2:660842439611:domain/delete-me-domain/*"
    ]
  }

  statement {
    sid = "AllowS3Access"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
    ]

    resources = [
      "${aws_s3_bucket.opensearch_s3_bucket.arn}",
      "${aws_s3_bucket.opensearch_s3_bucket.arn}/*",
    ]
  }

  statement {
    sid = "AllowKMSAccess"
    actions = [
      "kms:Decrypt",
      "kms:Encrypt",
      "kms:GenerateDataKey",
      "kms:DescribeKey",
    ]

    resources = [
      module.kms.key_arn,
    ]
  }
}

resource "aws_iam_policy" "opensearch_pipeline_policy" {
  name   = "${var.name}-pl-policy"
  policy = data.aws_iam_policy_document.opensearch_pipeline_policy_document.json
}

data "aws_iam_policy_document" "opensearch_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["osis-pipelines.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "opensearch_pipeline_role" {
  name               = "${var.name}-pl-role"
  assume_role_policy = data.aws_iam_policy_document.opensearch_assume_role.json
}

resource "aws_iam_policy_attachment" "opensearch_attachment" {
  name       = "${var.name}-pl-attachment"
  roles      = [aws_iam_role.opensearch_pipeline_role.name]
  policy_arn = aws_iam_policy.opensearch_pipeline_policy.arn
}
