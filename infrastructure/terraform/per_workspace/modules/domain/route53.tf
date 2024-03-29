data "aws_route53_zone" "zone" {
  name         = var.zone
  private_zone = false
}

resource "aws_route53_record" "route" {
  for_each = {
    for dvo in aws_acm_certificate.certificate.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.zone.zone_id
}


resource "aws_api_gateway_domain_name" "domain" {
  domain_name              = aws_acm_certificate.certificate.domain_name
  regional_certificate_arn = aws_acm_certificate_validation.validation.certificate_arn
  security_policy          = "TLS_1_2"
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  #   mutual_tls_authentication {
  #     truststore_uri     = "s3://${aws_s3_object.api_truststore.bucket}/${aws_s3_object.api_truststore.key}"
  #     truststore_version = aws_s3_object.api_truststore.version_id
  #   }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_acm_certificate_validation.validation
  ]
}

resource "aws_route53_record" "cname" {
  zone_id = data.aws_route53_zone.zone.id
  name    = var.domain
  type    = "CNAME"
  ttl     = "5"
  records = [
    aws_api_gateway_domain_name.domain.regional_domain_name
  ]
  allow_overwrite = true
  depends_on = [
    aws_acm_certificate.certificate
  ]
}
