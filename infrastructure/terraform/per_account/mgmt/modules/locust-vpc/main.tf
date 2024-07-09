data "aws_availability_zones" "available" {}

resource "aws_vpc" "locust_vpc" {
  cidr_block           = var.vpc_cidr_block
  instance_tenancy     = "default"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.prefix}-locust-vpc-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_subnet" "locust_public" {
  count             = var.subnet_count.public
  vpc_id            = aws_vpc.locust_vpc.id
  cidr_block        = element(var.public_subnet_cidr_blocks, count.index)
  availability_zone = element(data.aws_availability_zones.available.names, count.index)

  tags = {
    Name        = "${var.prefix}-locust-vpc-public-${var.environment}"
    Environment = var.environment
    Tier        = "public"
  }
}

resource "aws_internet_gateway" "locust_igw" {
  vpc_id = aws_vpc.locust_vpc.id

  tags = {
    Name = "locust-igw"
  }
}

resource "aws_route_table" "locust_route_table" {
  vpc_id = aws_vpc.locust_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.locust_igw.id
  }

  tags = {
    Name = "locust-route-table"
  }
}

resource "aws_route_table_association" "locust_vpc_public_association" {
  count          = length(aws_subnet.locust_public)
  subnet_id      = element(aws_subnet.locust_public.*.id, count.index)
  route_table_id = aws_route_table.locust_route_table.id
}

resource "aws_security_group" "locust_sg" {
  name        = "locust-security-group"
  description = "Allow HTTP and SSH traffic"
  vpc_id      = aws_vpc.locust_vpc.id

  tags = {
    Name        = "${var.prefix}-locust-vpc-sg-${var.environment}"
    Environment = var.environment
  }

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
  }

  ingress {
    from_port   = 8089
    to_port     = 8089
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5557
    to_port     = 5558
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

module "locust-bucket" {
  source                                = "terraform-aws-modules/s3-bucket/aws"
  version                               = "3.15.2"
  bucket                                = "${var.prefix}--locust-file"
  attach_deny_insecure_transport_policy = true
  force_destroy                         = true
  versioning = {
    enabled = true
  }
  tags = {
    Name = "${var.prefix}--locust-file"
  }
}
