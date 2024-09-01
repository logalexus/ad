variable "name" {
  description = "Name for VM"
  type        = string
}

variable "subnet_id" {
  description = "Subnet id from network"
  type        = string
}

variable "dns_zone_id" {
  description = "(Optional) - DNS zone id"
  type        = string
  default     = null
}

variable "ssh_keys" {
  description = "(Optional) - SSH keys for VM"
  type        = string
  default     = null
}

variable "use_external_ip" {
  description = "(Optional) - Use external IP"
  type        = string
  default     = false
}

variable "instance_resources" {
  description = "Resurces for instance VM"

  type = object({
    platform_id   = optional(string, "standard-v3")
    cores         = optional(number, 2)
    memory        = optional(number, 2)
    core_fraction = optional(number, 100)
    disk = optional(object({
      image_id  = optional(string, "fd8gqkbp69nel2ibb5pr")
      disk_type = optional(string, "network-ssd")
      disk_size = optional(number, 15)
    }), {})
  })
}
