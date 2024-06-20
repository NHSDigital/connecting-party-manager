resource "aws_opensearch_domain" "opensearch_domain" {
  domain_name    = "${var.name}-domain"
  engine_version = "OpenSearch_2.13"

  cluster_config {
    instance_type = "m6g.large.search"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "search_admin"
      master_user_password = "letMe1n!" # pragma: allowlist secret
    }
    # This is horrible ^
  }

  encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  node_to_node_encryption {
    enabled = true
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 100
  }

  tags = {
    Name = replace(var.name, "_", "-")
  }

}

data "aws_iam_policy_document" "opensearch_policy_document" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions   = ["es:*"]
    resources = ["${aws_opensearch_domain.opensearch_domain.arn}/*"]

    # condition {
    #   test     = "IpAddress"
    #   variable = "aws:SourceIp"
    #   values   = ["127.0.0.1/32"]
    # }

  }

}

resource "aws_opensearch_domain_policy" "opensearch_policy" {
  domain_name     = aws_opensearch_domain.opensearch_domain.domain_name
  access_policies = data.aws_iam_policy_document.opensearch_policy_document.json
  depends_on      = [time_sleep.delay_2_min]
}


resource "time_sleep" "delay_2_min" {
  create_duration = "2m"

  depends_on = [aws_opensearch_domain.opensearch_domain]
}
