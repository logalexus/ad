locals {
  vms = [
    "team1", 
    "team2", 
    "team3", 
  ]
}

module "vuln" {
  source      = "../modules/vm"
  for_each    = toset(local.vms)
  name        = each.key
  subnet_id   = yandex_vpc_subnet.ad-subnet.id
  use_external_ip = true
  instance_resources = {
    cores  = 4
    memory = 4
    disk = {
      disk_size = 50
    }
  }
}

module "jury" {
  source      = "../modules/vm"
  name        = "jury"
  subnet_id   = yandex_vpc_subnet.ad-subnet.id
  use_external_ip = true
  instance_resources = {
    cores  = 4
    memory = 4
    disk = {
      disk_size = 30
    }
  }
}

module "vpn" {
  source          = "../modules/vm"
  name            = "advpn"
  subnet_id       = yandex_vpc_subnet.ad-subnet.id
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

resource "yandex_vpc_network" "ad-net" {
  name        = "network-ad"
  description = "AD network"
}

resource "yandex_vpc_subnet" "ad-subnet" {
  name           = "subnet-ad"
  description    = "AD subnet"
  v4_cidr_blocks = ["10.2.0.0/16"]
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.ad-net.id
  route_table_id = yandex_vpc_route_table.rt.id
}

resource "yandex_vpc_gateway" "nat_gateway" {
  name = "ad-gateway"
  shared_egress_gateway {}
}

resource "yandex_vpc_route_table" "rt" {
  name       = "ad-route-table"
  network_id = yandex_vpc_network.ad-net.id

  static_route {
    destination_prefix = "0.0.0.0/0"
    gateway_id         = yandex_vpc_gateway.nat_gateway.id
  }
}

