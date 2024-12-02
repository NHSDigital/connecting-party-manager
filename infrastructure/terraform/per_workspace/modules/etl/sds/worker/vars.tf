variable "workspace_prefix" {
  type = string
}

variable "etl_name" {
  type = string
}

variable "etl_type" {
  type = string
}


variable "etl_stage" {
  type = string
}

variable "python_version" {
  type = string
}

variable "etl_bucket_name" {
  type    = string
  default = ""
}

variable "layers" {
  type = list(string)
}
variable "assume_account" {
  type = string
}

variable "environment_variables" {
  default = {}
}

variable "policy_json" {
  default = <<-EOT
      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Sid": "nullPolicy",
                  "Effect": "Allow",
                  "Action": "none:null",
                  "Resource": "*"
              }
          ]
      }
    EOT
}
