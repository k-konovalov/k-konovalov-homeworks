# Подход: сеть/подсеть VPC в Yandex → Proxmox

## Yandex

```hcl
resource "yandex_vpc_network" "net-1" { }
resource "yandex_vpc_subnet" "subnet-1" {
  network_id     = yandex_vpc_network.net-1.id
  v4_cidr_blocks = ["10.0.0.0/24"]
}
```

## Proxmox

Ресурсов VPC-сети и подсети **нет**. Роль сети выполняет **мост** на гипервизоре,
задаваемый строкой в `network_device.bridge` (обычно `vmbr0`).

Сетевые настройки гостевой ОС (CIDR, шлюз, DNS) — через cloud-init:

```hcl
network_device {
  bridge  = "vmbr0"
  enabled = true
}

initialization {
  ip_config {
    ipv4 {
      address = "10.0.0.5/24"
      gateway = "10.0.0.1"
    }
  }
  dns {
    servers = ["8.8.8.8"]
  }
}
```

VLAN-тегирование: `network_device.vlan_id`, `network_device.trunks`.

## Решение

Сеть описывается мостом + cloud-init; отдельного ресурса подсети нет.
Для DHCP можно опустить `ip_config` и оставить `bridge`, адрес выдаст DHCP.