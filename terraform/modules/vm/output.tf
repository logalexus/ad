output "instance_public_ip_address" {
  description = "The external IP address of the instance."
  value       = yandex_compute_instance.vm.network_interface.0.nat_ip_address
}

output "instance_private_ip_address" {
  description = "The external IP address of the instance."
  value       = yandex_compute_instance.vm.network_interface.0.ip_address
}

output "instance_id" {
  description = "Instance ID"
  value       = yandex_compute_instance.vm.id
}

output "dns_name" {
  description = "DNS name"
  value       = yandex_compute_instance.vm.network_interface.0.dns_record
}
