locals {
  zone            = "ru-central1-a"
  default_ssh_key = "ubuntu:${file("~/.ssh/id_rsa.pub")}"
  ssh_key_to_use  = var.ssh_keys != null ? var.ssh_keys : local.default_ssh_key
}

resource "yandex_compute_disk" "boot_disk" {
  name     = "${var.name}-boot-disk"
  zone     = local.zone
  image_id = var.instance_resources.disk.image_id
  type     = var.instance_resources.disk.disk_type
  size     = var.instance_resources.disk.disk_size
}

resource "yandex_compute_instance" "vm" {
  name        = var.name
  hostname    = var.name
  platform_id = var.instance_resources.platform_id
  zone        = local.zone

  resources {
    cores         = var.instance_resources.cores
    memory        = var.instance_resources.memory
    core_fraction = var.instance_resources.core_fraction
  }

  boot_disk {
    disk_id = yandex_compute_disk.boot_disk.id
  }

  network_interface {
    subnet_id = var.subnet_id
    nat       = var.use_external_ip
  }

  metadata = {
    ssh-keys = local.ssh_key_to_use
  }

  scheduling_policy {
    preemptible = true
  }
}

resource "yandex_dns_recordset" "rs1" {
  count   = var.dns_zone_id != null ? 1 : 0
  zone_id = var.dns_zone_id
  name    = var.name
  type    = "A"
  ttl     = 200
  data    = [yandex_compute_instance.vm.network_interface.0.ip_address]
}
