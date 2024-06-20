data "aws_opensearch_domain" "opensearch_domain" {
  domain_name = aws_opensearch_domain.opensearch_domain.domain_name
}
