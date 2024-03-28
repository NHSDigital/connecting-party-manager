data "aws_availability_zones" "available" {}

data "aws_secretsmanager_secret_version" "sds-ldap-endpoint" {
  secret_id = "${terraform.workspace}-sds-ldap-endpoint"
}

#------------------------------------------------------------------------------
# VPC
#------------------------------------------------------------------------------

resource "aws_vpc" "lambda-connectivity" {
  cidr_block           = var.vpc_cidr_block
  instance_tenancy     = "default"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.prefix}-lambda-connectivity-vpc-${var.environment}"
    Environment = var.environment
  }
}

#------------------------------------------------------------------------------
# Subnets
#------------------------------------------------------------------------------

resource "aws_subnet" "lambda-connectivity-private" {
  count             = var.subnet_count.private
  vpc_id            = aws_vpc.lambda-connectivity.id
  cidr_block        = element(var.private_subnet_cidr_blocks, count.index)
  availability_zone = element(data.aws_availability_zones.available.names, count.index)

  tags = {
    Name        = "${var.prefix}-lambda-connectivity-private-${var.environment}"
    Environment = var.environment
    Tier        = "private"
  }
}

# #------------------------------------------------------------------------------
# # Security Groups
# #------------------------------------------------------------------------------

resource "aws_security_group" "sds-ldap" {
  name        = "${var.prefix}-sds-ldap-${var.environment}"
  description = "Default security group for ${var.prefix} lambda connectivity VPC"
  vpc_id      = aws_vpc.lambda-connectivity.id

  tags = {
    Name        = "${var.prefix}-sds-ldap-${var.environment}"
    Environment = var.environment
  }

  # read to s3
  # write to s3
  # read from hscn

}

#------------------------------------------------------------------------------
# Route Table
#------------------------------------------------------------------------------

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.lambda-connectivity.id
}

resource "aws_route_table_association" "private" {
  count          = var.subnet_count.private
  subnet_id      = element(aws_subnet.lambda-connectivity-private, count.index).id
  route_table_id = aws_route_table.private.id
}

#------------------------------------------------------------------------------
# VPC endpoints
#------------------------------------------------------------------------------

resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.lambda-connectivity.id
  service_name = "com.amazonaws.eu-west-2.s3"

  tags = {
    Name        = "s3-vpc-endpoint"
    Environment = var.environment
  }
}

resource "aws_vpc_endpoint_route_table_association" "s3" {
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
  route_table_id  = aws_route_table.private.id
}

resource "aws_vpc_endpoint" "hscn_endpoint" {
  vpc_id            = aws_vpc.lambda-connectivity.id
  vpc_endpoint_type = "Interface"
  service_name      = data.aws_secretsmanager_secret_version.sds-ldap-endpoint.secret_string

  tags = {
    Name        = "ldap-vpc-endpoint"
    Environment = var.environment
  }
}

resource "aws_vpc_endpoint_security_group_association" "hscn_endpoint" {
  vpc_endpoint_id   = aws_vpc_endpoint.hscn_endpoint.id
  security_group_id = aws_security_group.sds-ldap.id
}
