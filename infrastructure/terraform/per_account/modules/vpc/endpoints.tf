module "endpoints" {
  source  = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  version = "5.5.3"

  vpc_id             = aws_vpc.lambda-connectivity.id
  security_group_ids = [aws_vpc.lambda-connectivity.default_security_group_id]

  endpoints = {
    s3 = {
      # interface endpoint
      service = "s3"
    },
  }

  tags = {
    Environment = var.environment
  }
}
