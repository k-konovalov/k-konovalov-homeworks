#
# Rewritten from itmo/ITMO/itmo_OS/terraform.d/yandex/01.main.tf
# for the bpg/proxmox provider (см. YA_TO_PROXMOX/SKILL.md).
#
# Mapping notes (yandex -> proxmox):
#   yandex_vpc_network / yandex_vpc_subnet  -> network bridge (vmbr0),
#                                              нет отдельного ресурса сети/подсети;
#                                              статический CIDR задаётся через cloud-init
#   yandex_compute_disk.boot-disk-1 (image) -> proxmox_virtual_environment_download_file
#                                              + блок disk
#   yandex_compute_instance                 -> proxmox_virtual_environment_vm
#   platform_id (standard-v3)               -> cpu { type = "x86-64-v2-AES" }
#   resources.cores = 2                     -> cpu { cores = 2, sockets = 1 }
#   resources.memory = 2 (GB)               -> memory { dedicated = 2048 } (MiB)
#   resources.core_fraction = 20            -> cpu { limit = 20 } (процент лимита)
#   boot_disk                               -> disk { interface = "scsi0", ... }
#   network_interface.subnet_id             -> network_device { bridge = "vmbr0" }
#   network_interface.nat = true            -> bridge + QEMU agent для чтения IP
#

# Image: yandex_compute_disk.boot-disk-1.image_id (fd80tpcdvop5e9qcosnq)
# In Proxmox the OS image is downloaded into a datastore and then attached as a disk.
resource "proxmox_download_file" "vm-1-image" {
  content_type = "iso"
  datastore_id = "local"
  node_name    = "pve"
  url          = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2"
}

resource "proxmox_virtual_environment_vm" "vm-1002" {
  name      = "vm-1002"
  node_name = "pve"

  # Start the VM after creation (Yandex default is running).
  started = true
  on_boot = false

  # QEMU agent: allows Terraform to read guest IP addresses
  # (equivalent to how Yandex publishes VM addresses / nat = true).
  agent {
    enabled = true
  }

  # Equivalent of: platform_id = "standard-v3", resources { cores = 2, core_fraction = 20 }.
  cpu {
    cores   = 2
    sockets = 1
    type    = "x86-64-v2-AES"
    limit   = 20   # core_fraction = 20 (процент гарантированной доли vCPU)
  }

  # Yandex memory is in GB (2), Proxmox expects MiB (2048).
  memory {
    dedicated = 2048
  }

  # Equivalent of the boot disk yandex_compute_disk.boot-disk-1 (image + 20 ГБ).
  disk {
    interface    = "scsi0"
    datastore_id = "local-lvm"
    size         = 2
    file_id      = proxmox_download_file.vm-1-image.id
  }

  # Equivalent of network_interface { subnet_id = ..., nat = true }.
  # In Proxmox networking is attached via a bridge (default vmbr0).
  network_device {
    bridge  = "vmbr0"
  }

  # Static addressing from yandex_vpc_subnet.subnet-1 (192.168.10.0/24).
  # Optional: omit ip_config to rely on DHCP of the bridge.
  initialization {
    ip_config {
      ipv4 {
        address = "192.168.10.10/24"
        gateway = "192.168.10.1"
      }
    }
    dns {
      servers = ["8.8.8.8"]
    }
  }
}