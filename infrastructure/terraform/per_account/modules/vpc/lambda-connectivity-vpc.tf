data "aws_availability_zones" "available" {}


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
    Name        = "${var.prefix}-private-subnet-${count.index}-${var.environment}"
    Environment = var.environment
    Tier        = "private"
  }
}
