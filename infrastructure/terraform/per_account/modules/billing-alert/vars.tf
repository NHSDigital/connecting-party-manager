variable "prefix" {
  type = string
}

variable "threshold_dollars" {
  type = number
}
variable "recipients" {
  type = list(string)
}

variable "metric_name" {
  type = string
}

variable "metric_number_of_evaluation_periods" {
  type = number
}

variable "metric_statistic" {
  type = string
}

variable "tags" {

}
