data "aws_secretsmanager_secret_version" "sds-ldap-endpoint" {
  secret_id = "${terraform.workspace}-sds-ldap-endpoint"
}

module "endpoints" {
  source  = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  version = "5.5.3"

  vpc_id             = aws_vpc.lambda-connectivity.id
  security_group_ids = [aws_vpc.lambda-connectivity.default_security_group_id]

  endpoints = {
    s3 = {
      service_name = "s3"
    },
    ldap_endpoint = {
      service_endpoint = data.aws_secretsmanager_secret_version.sds-ldap-endpoint
    }
  }

  tags = {
    Environment = var.environment
  }
}
