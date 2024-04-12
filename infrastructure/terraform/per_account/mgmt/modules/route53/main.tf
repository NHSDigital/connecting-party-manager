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

# resource "aws_route53_record" "prod_zone" {
#   zone_id = module.zones.route53_zone_zone_id["cpm.national.nhs.uk"]
#   name    = "api.cpm.national.nhs.uk"
#   records = [
#     "ns-453.awsdns-56.com.",
#     "ns-980.awsdns-58.net.",
#     "ns-1983.awsdns-55.co.uk.",
#     "ns-1103.awsdns-09.org."
#   ]
#   ttl  = 300
#   type = "NS"
# }

resource "aws_route53_record" "dev_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.dev.national.nhs.uk"]
  name    = "api.cpm.dev.national.nhs.uk"
  records = [
    "ns-821.awsdns-38.net.",
    "ns-1945.awsdns-51.co.uk.",
    "ns-366.awsdns-45.com.",
    "ns-1311.awsdns-35.org.",
  ]
  ttl  = 300
  type = "NS"
}

resource "aws_route53_record" "qa_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.qa.national.nhs.uk"]
  name    = "api.cpm.qa.national.nhs.uk"
  records = [
    "ns-488.awsdns-61.com.",
    "ns-1386.awsdns-45.org.",
    "ns-1805.awsdns-33.co.uk.",
    "ns-992.awsdns-60.net."
  ]
  ttl  = 300
  type = "NS"
}

resource "aws_route53_record" "int_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.int.national.nhs.uk"]
  name    = "api.cpm.int.national.nhs.uk"
  records = [
    "ns-1155.awsdns-16.org.",
    "ns-1601.awsdns-08.co.uk.",
    "ns-259.awsdns-32.com.",
    "ns-742.awsdns-28.net."
  ]
  ttl  = 300
  type = "NS"
}

resource "aws_route53_record" "ref_zone" {
  zone_id = module.zones.route53_zone_zone_id["cpm.ref.national.nhs.uk"]
  name    = "api.cpm.ref.national.nhs.uk"
  records = [
    "ns-1032.awsdns-01.org.",
    "ns-1703.awsdns-20.co.uk.",
    "ns-698.awsdns-23.net.",
    "ns-20.awsdns-02.com."
  ]
  ttl  = 300
  type = "NS"
}
