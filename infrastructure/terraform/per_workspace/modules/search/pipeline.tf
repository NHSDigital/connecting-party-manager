resource "aws_osis_pipeline" "opensearch_pipeline" {
  pipeline_name               = "${var.name}-pl"
  pipeline_configuration_body = file("${path.module}/pipeline_policy.yaml")
  max_units                   = 1
  min_units                   = 1

  depends_on = [
    aws_iam_role.opensearch_pipeline_role,
    aws_iam_policy_attachment.opensearch_attachment,
    aws_s3_bucket.opensearch_s3_bucket
  ]
}
