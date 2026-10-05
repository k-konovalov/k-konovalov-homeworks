#
# Rewritten from itmo/ITMO/itmo_OS/terraform.d/yandex/00.main.tf
# for the bpg/proxmox provider (см. SKILL.yandex-to-proxmox.md).
#
# Mapping notes (yandex -> proxmox):
#   yandex_compute_instance          -> proxmox_virtual_environment_vm
#   resources.cores = 1              -> cpu { cores = 1, sockets = 1 }
#   resources.memory = 2 (GB)        -> memory { dedicated = 2048 } (MiB)
#   boot_disk                        -> disk { interface = "scsi0", ... }
#   network_interface.subnet_id      -> network_device { bridge = "vmbr0" }
#   network_interface.nat = true     -> bridge provides network access;
#                                       enable QEMU agent to query IPs
#
resource "proxmox_virtual_environment_vm" "vm-1001" {
  name      = "vm-1001"
  node_name = "pve"

  # Start the VM after creation (Yandex default is running).
  started = true

  # QEMU agent: allows Terraform to read guest IP addresses
  # (equivalent to how Yandex publishes VM addresses).
  agent {
    enabled = true
  }

  # Equivalent of: resources { cores = 1, memory = 2 }
  cpu {
    cores   = 1
    sockets = 1
  }

  # Yandex memory is in GB (2), Proxmox expects MiB (2048).
  memory {
    dedicated = 2048
  }

  # Equivalent of the boot disk yandex_compute_disk.boot-уdisk-1.
  # A fresh boot disk on the project storage (defaults to local-lvm).
  disk {
    interface    = "scsi0"
    datastore_id = "local-lvm"
    size         = 2
  }

  # Equivalent of network_interface { subnet_id = ... , nat = true }.
  # In Proxmox networking is attached via a bridge (default vmbr0).
  network_device {
    bridge  = "vmbr0"
    enabled = true
  }
}