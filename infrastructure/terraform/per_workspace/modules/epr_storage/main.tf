# module "vpc" {
#   source  = "terraform-aws-modules/vpc/aws"
#   version = "5.5.3"
#
#   name = "${var.name}-vpc"
#   cidr = "10.0.0.0/16"
#
#   azs           = ["eu-west-2a", "eu-west-2b", "eu-west-2c"]
#   intra_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
#
#   tags = {
#     Name = "${var.name}-vpc"
#   }
# }

# module "aurora" {
#   source  = "terraform-aws-modules/rds-aurora/aws"
#   version = "9.0.2"
# }
#

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "${var.name}-vpc"
  }
}


resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "Main"
  }
}


resource "aws_security_group" "lambda_sg" {
  vpc_id = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lambda-security-group"
  }
}

resource "aws_security_group" "rds_sg" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  tags = {
    Name = "rds-security-group"
  }
}

resource "aws_db_subnet_group" "aurora_subnet_group" {
  name       = "aurora-subnet-group"
  subnet_ids = [aws_subnet.main.id]

  tags = {
    Name = "aurora-subnet-group"
  }
}

resource "aws_rds_cluster" "aurora" {
  cluster_identifier     = "aurora-cluster"
  engine                 = "aurora-mysql"
  engine_version         = "8.0.mysql_aurora.3.03.1"
  database_name          = "mydatabase"
  master_username        = "admin"
  skip_final_snapshot    = true
  db_subnet_group_name   = aws_db_subnet_group.aurora_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  tags = {
    Name = "aurora-cluster"
  }
}
