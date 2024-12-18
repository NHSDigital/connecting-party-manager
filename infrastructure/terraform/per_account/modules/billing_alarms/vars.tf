variable "limit" {
  type    = string
  default = "1000"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "email_subscribers" {
  type = set(string)
  default = [
    "james.linnell@burendo.com",
    # "james.linnell2@nhs.net",
    # "rowan.gill1@nhs.net"
  ]
}
