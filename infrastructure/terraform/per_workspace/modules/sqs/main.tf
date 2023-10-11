module "sqs" {
  source = "terraform-aws-modules/sqs/aws"

  name = var.name

  tags = {
    Environment = "dev"
  }
}
