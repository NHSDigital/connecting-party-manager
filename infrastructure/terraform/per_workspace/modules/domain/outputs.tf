output "zone" {
  value = var.zone
}

output "domain" {
  value = var.domain
}

output "domain_cert" {
  value = "https://${aws_acm_certificate.certificate.domain_name}"
}
