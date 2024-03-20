data "aws_availability_zones" "available" {}

#------------------------------------------------------------------------------
# VPC
#------------------------------------------------------------------------------

resource "aws_vpc" "lambda-connectivity-vpc" {
  cidr_block           = var.vpc_cidr_block
  instance_tenancy     = "default"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${local.project}-lambda-connectivity-vpc-${local.environment}"
    Environment = local.environment
  }
}

#------------------------------------------------------------------------------
# Subnets
#------------------------------------------------------------------------------

resource "aws_subnet" "private-subnet" {
  count             = var.subnet_count.private
  vpc_id            = aws_vpc.lambda-connectivity-vpc.id
  cidr_block        = element(var.private_subnet_cidr_blocks, count.index)
  availability_zone = element(data.aws_availability_zones.available.names, count.index)

  tags = {
    Name        = "${local.project}-private-subnet-${count.index}-${local.environment}"
    Environment = local.environment
    Tier        = "private"
  }
}
