locals {
  region       = "eu-west-2"
  project      = "nhse-cpm"
  current_time = timestamp()
  zone_name    = sort(keys(module.zones.route53_zone_zone_id))[0]
}
