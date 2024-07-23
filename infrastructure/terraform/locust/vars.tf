variable "aws_region" {
  description = "The AWS region to deploy to"
  default     = "eu-west-2"
}

variable "instance_type" {
  description = "The EC2 instance type"
  default     = "t3.medium"
}

variable "locust_file" {
  description = "The path to the Locust file"
  default     = "locustfile.py"
}

variable "worker_count" {
  description = "The number of worker nodes"
  default     = 3
}

variable "environment" {
  default = "mgmt"
}
