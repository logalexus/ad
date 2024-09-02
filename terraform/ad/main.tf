locals {
  subnet_id   = "e9b2hvniretjviruoq61"
  dns_zone_id = "dns8jg2ig5tgnkhu0h54"
  vms = [
    "team1", 
    "team2", 
  ]
}

module "vuln" {
  source      = "../modules/vm"
  for_each    = toset(local.vms)
  name        = each.key
  subnet_id   = local.subnet_id
  dns_zone_id = local.dns_zone_id
  instance_resources = {
    cores  = 4
    memory = 4
  }
}

module "jury" {
  source      = "../modules/vm"
  name        = "jury"
  subnet_id   = local.subnet_id
  dns_zone_id = local.dns_zone_id
  instance_resources = {
    cores  = 4
    memory = 4
  }
}

module "vpn" {
  source          = "../modules/vm"
  name            = "advpn"
  subnet_id       = local.subnet_id
  dns_zone_id     = local.dns_zone_id
  use_external_ip = true
  instance_resources = {
    platform_id   = "standard-v2"
    cores         = 2
    memory        = 2
    disk = {
      disk_type = "network-hdd"
      disk_size = 10
    }
  }
}

