
resource "aws_s3_bucket" "opensearch_s3_bucket" {
  bucket = "${var.name}-bucket"
}
