resource "aws_iam_role" "locust_role" {
  name = "locust_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "locust_policy" {
  name        = "locust_policy"
  description = "Policy for Locust EC2 instances to access S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:GetObject"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:s3:::nhse-cpm--mgmt--locust-file/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "locust_role_policy_attachment" {
  role       = aws_iam_role.locust_role.name
  policy_arn = aws_iam_policy.locust_policy.arn
}

resource "aws_iam_instance_profile" "locust_profile" {
  name = "locust_profile"
  role = aws_iam_role.locust_role.name
}
