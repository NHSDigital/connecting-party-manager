variable "python_version" {
  default = "python3.11"
}

variable "lambda_name" {}

variable "layers" {
  type = list(string)
}

variable "source_path" {}