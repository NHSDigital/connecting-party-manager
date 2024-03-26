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
      service = "s3"
      tags    = { Name = "s3-vpc-endpoint" }
    },
    hscn_endpoint = {
      service_name     = data.aws_secretsmanager_secret_version.sds-ldap-endpoint.secret_string
      service_endpoint = data.aws_secretsmanager_secret_version.sds-ldap-endpoint.secret_string
      tags             = { Name = "ldap-vpc-endpoint" }
    }
  }

  tags = {
    Environment = var.environment
  }
}
