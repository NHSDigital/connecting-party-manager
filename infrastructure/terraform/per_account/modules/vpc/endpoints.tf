data "aws_secretsmanager_secret_version" "sds-ldap-endpoint" {
  secret_id = "${terraform.workspace}-sds-ldap-endpoint"
}

locals {
  sds_ldap_endpoint_parse = split(".", data.aws_secretsmanager_secret_version.sds-ldap-endpoint.secret_string)
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
    # Retrieve service name from secretsmanager
    "${local.sds_ldap_endpoint_parse[4]}" = {
      service_name = data.aws_secretsmanager_secret_version.sds-ldap-endpoint.secret_string
      # service_endpoint = data.aws_secretsmanager_secret_version.sds-ldap-endpoint.secret_string
      tags = { Name = "ldap-vpc-endpoint" }
    }
  }

  tags = {
    Environment = var.environment
  }
}
