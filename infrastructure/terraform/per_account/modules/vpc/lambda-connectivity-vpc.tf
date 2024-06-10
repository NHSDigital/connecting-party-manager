data "aws_availability_zones" "available" {}

data "aws_secretsmanager_secret_version" "sds-hscn-endpoint" {
  secret_id = "${terraform.workspace}-sds-hscn-endpoint"
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
  description = "Default security group for ${var.prefix} lambda connectivity VPC endpoint"
  vpc_id      = aws_vpc.lambda-connectivity.id

  tags = {
    Name        = "${var.prefix}-sds-ldap-${var.environment}"
    Environment = var.environment
  }

  # Inbound rule: Allow traffic from the LDAP server
  ingress {
    from_port   = 636
    to_port     = 636
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"] # restrict this?
  }

  # Outbound rule: Allow traffic to the LDAP server
  egress {
    from_port   = 636
    to_port     = 636
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # restrict this?
  }
  # Inbound rule: Allow traffic from s3
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Outbound rule: Allow traffic to s3
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }
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
    Name        = "${var.prefix}-s3-vpc-endpoint-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_vpc_endpoint_route_table_association" "s3" {
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
  route_table_id  = aws_route_table.private.id
}

resource "aws_vpc_endpoint" "hscn_endpoint" {
  vpc_id              = aws_vpc.lambda-connectivity.id
  vpc_endpoint_type   = "Interface"
  service_name        = data.aws_secretsmanager_secret_version.sds-hscn-endpoint.secret_string
  private_dns_enabled = true

  tags = {
    Name        = "${var.prefix}-hscn-vpc-endpoint-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_vpc_endpoint_subnet_association" "hscn_endpoint" {
  count           = var.subnet_count.private
  vpc_endpoint_id = aws_vpc_endpoint.hscn_endpoint.id
  subnet_id       = element(aws_subnet.lambda-connectivity-private, count.index).id
}

resource "aws_vpc_endpoint_security_group_association" "hscn_endpoint" {
  vpc_endpoint_id   = aws_vpc_endpoint.hscn_endpoint.id
  security_group_id = aws_security_group.sds-ldap.id
}

resource "aws_vpc_endpoint" "state_machine" {
  vpc_id              = aws_vpc.lambda-connectivity.id
  vpc_endpoint_type   = "Interface"
  service_name        = "com.amazonaws.eu-west-2.states"
  private_dns_enabled = true

  tags = {
    Name        = "${var.prefix}-state-machine-vpc-endpoint-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_vpc_endpoint_subnet_association" "state_machine" {
  count           = var.subnet_count.private
  vpc_endpoint_id = aws_vpc_endpoint.state_machine.id
  subnet_id       = element(aws_subnet.lambda-connectivity-private, count.index).id
}

resource "aws_vpc_endpoint_security_group_association" "state_machine" {
  vpc_endpoint_id   = aws_vpc_endpoint.state_machine.id
  security_group_id = aws_security_group.sds-ldap.id
}


resource "aws_vpc_endpoint" "notify_lambda" {
  vpc_id              = aws_vpc.lambda-connectivity.id
  vpc_endpoint_type   = "Interface"
  service_name        = "com.amazonaws.eu-west-2.lambda"
  private_dns_enabled = true

  tags = {
    Name        = "${var.prefix}-notify-lambda-vpc-endpoint-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_vpc_endpoint_subnet_association" "notify_lambda" {
  count           = var.subnet_count.private
  vpc_endpoint_id = aws_vpc_endpoint.notify_lambda.id
  subnet_id       = element(aws_subnet.lambda-connectivity-private, count.index).id
}

resource "aws_vpc_endpoint_security_group_association" "notify_lambda" {
  vpc_endpoint_id   = aws_vpc_endpoint.notify_lambda.id
  security_group_id = aws_security_group.sds-ldap.id
}

resource "aws_vpc_endpoint" "sqs" {
  vpc_id              = aws_vpc.lambda-connectivity.id
  vpc_endpoint_type   = "Interface"
  service_name        = "com.amazonaws.eu-west-2.sqs"
  private_dns_enabled = true

  tags = {
    Name        = "${var.prefix}-sqs-vpc-endpoint-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_vpc_endpoint_subnet_association" "sqs" {
  count           = var.subnet_count.private
  vpc_endpoint_id = aws_vpc_endpoint.sqs.id
  subnet_id       = element(aws_subnet.lambda-connectivity-private, count.index).id
}

resource "aws_vpc_endpoint_security_group_association" "sqs" {
  vpc_endpoint_id   = aws_vpc_endpoint.sqs.id
  security_group_id = aws_security_group.sds-ldap.id
}
