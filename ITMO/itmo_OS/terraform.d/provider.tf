terraform {
  required_providers {
    proxmox = {
      source = "bpg/proxmox"
    }
  }
}

provider "proxmox" {
  endpoint   = var.virtual_environment_endpoint
  username   = var.virtual_environment_username
  password   = var.virtual_environment_root_password
  insecure   = true
}