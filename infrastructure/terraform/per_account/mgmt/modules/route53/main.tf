module "zones" {
  source  = "terraform-aws-modules/route53/aws//modules/zones"
  version = "2.11.0"

  zones = {
    "cpm.national.nhs.uk" = {
      comment = "Connecting Party Manager Production Zone."
      tags = {
        Name = "${local.project}--${replace(var.workspace, "_", "-")}--dns-prod-zone"
      }
    },
    "cpm.dev.national.nhs.uk" = {
      comment = "Connecting Party Manager Dev Zone."
      tags = {
        Name = "${local.project}--${replace(var.workspace, "_", "-")}--dns-dev-zone"
      }
    },
    "cpm.qa.national.nhs.uk" = {
      comment = "Connecting Party Manager QA Zone."
      tags = {
        Name = "${local.project}--${replace(var.workspace, "_", "-")}--dns-qa-zone"
      }
    },
    "cpm.int.national.nhs.uk" = {
      comment = "Connecting Party Manager Int Zone."
      tags = {
        Name = "${local.project}--${replace(var.workspace, "_", "-")}--dns-int-zone"
      }
    },
    "cpm.ref.national.nhs.uk" = {
      comment = "Connecting Party Manager Ref Zone."
      tags = {
        Name = "${local.project}--${replace(var.workspace, "_", "-")}--dns-ref-zone"
      }
    }
  }

}

resource "aws_route53_record" "prod_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.national.nhs.uk"]
  name    = "api.cpm.national.nhs.uk"
  records = [
    "ns-453.awsdns-56.com.",
    "ns-980.awsdns-58.net.",
    "ns-1983.awsdns-55.co.uk.",
    "ns-1103.awsdns-09.org."
  ]
  ttl  = 300
  type = "NS"
}

resource "aws_route53_record" "dev_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.dev.national.nhs.uk"]
  name    = "api.cpm.dev.national.nhs.uk"
  records = [
    "ns-1028.awsdns-00.org.",
    "ns-201.awsdns-25.com.",
    "ns-2007.awsdns-58.co.uk.",
    "ns-823.awsdns-38.net."
  ]
  ttl  = 300
  type = "NS"
}

resource "aws_route53_record" "qa_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.qa.national.nhs.uk"]
  name    = "api.cpm.qa.national.nhs.uk"
  records = [
    "ns-286.awsdns-35.com.",
    "ns-596.awsdns-10.net.",
    "ns-1571.awsdns-04.co.uk.",
    "ns-1244.awsdns-27.org."
  ]
  ttl  = 300
  type = "NS"
}

resource "aws_route53_record" "int_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.int.national.nhs.uk"]
  name    = "api.cpm.int.national.nhs.uk"
  records = [
    "ns-1843.awsdns-38.co.uk.",
    "ns-1350.awsdns-40.org.",
    "ns-1020.awsdns-63.net.",
    "ns-26.awsdns-03.com."
  ]
  ttl  = 300
  type = "NS"
}

resource "aws_route53_record" "ref_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.ref.national.nhs.uk"]
  name    = "api.cpm.ref.national.nhs.uk"
  records = [
    "ns-287.awsdns-35.com.",
    "ns-1587.awsdns-06.co.uk.",
    "ns-1109.awsdns-10.org.",
    "ns-746.awsdns-29.net."
  ]
  ttl  = 300
  type = "NS"
}
