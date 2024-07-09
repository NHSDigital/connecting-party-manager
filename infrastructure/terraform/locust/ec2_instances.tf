data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

data "aws_subnets" "locust_vpc_public" {
  filter {
    name   = "tag:Name"
    values = ["${local.prefix}-locust-vpc-public-${var.environment}"]
  }
}

data "aws_security_group" "locust_vpc_sg" {
  id = "sg-0897f0fba952137f0"
}

data "aws_key_pair" "locust_key" {
  key_name = "locust-key"
}

data "aws_iam_instance_profile" "locust_profile" {
  name = "locust_profile"
}

resource "aws_instance" "locust_master" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = data.aws_key_pair.locust_key.key_name
  subnet_id                   = element(data.aws_subnets.locust_vpc_public.ids, 0)
  associate_public_ip_address = true
  security_groups             = [data.aws_security_group.locust_vpc_sg.id]
  iam_instance_profile        = data.aws_iam_instance_profile.locust_profile.name

  tags = {
    Name = "LocustMaster"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y python3-pip
              sudo apt-get install -y awscli
              aws s3 cp s3://nhse-cpm--mgmt--locust-file/locustfile.py .
              pip3 install locust
              EOF
}

resource "aws_instance" "locust_worker" {
  count                       = var.worker_count
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = data.aws_key_pair.locust_key.key_name
  subnet_id                   = element(data.aws_subnets.locust_vpc_public.ids, count.index % length(data.aws_subnets.locust_vpc_public.ids))
  associate_public_ip_address = true
  security_groups             = [data.aws_security_group.locust_vpc_sg.id]
  iam_instance_profile        = data.aws_iam_instance_profile.locust_profile.name

  tags = {
    Name = "LocustWorker${count.index}"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y python3-pip
              sudo apt-get install -y awscli
              aws s3 cp s3://nhse-cpm--mgmt--locust-file/locustfile.py .
              pip3 install locust
              EOF
}
