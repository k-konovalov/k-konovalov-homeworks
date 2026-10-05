resource "yandex_compute_instance" "vm-1" {
  name = "vm-1"

  resources {
    cores  = 1
    memory = 2
  }

  boot_disk {
    disk_id = yandex_compute_disk.boot-disk-1.id
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet-1.id
    nat       = true
  }
} 