variable "aws_region" {
  description = "The AWS region to deploy to"
  default     = "eu-west-2"
}

variable "vpc_cidr_block" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_count" {
  description = "Number of subnets"
  type        = map(number)
  default = {
    public = 3
  }
}

variable "public_subnet_cidr_blocks" {
  description = "Available CIDR blocks for poublic subnets"
  type        = list(string)
  default = [
    "10.0.101.0/24",
    "10.0.102.0/24",
    "10.0.103.0/24"
  ]
}

variable "environment" {
}
variable "prefix" {
}
