# Подход: `nat = true` (публичный IP) в Yandex → Proxmox

## Yandex

```hcl
network_interface {
  subnet_id = yandex_vpc_subnet.subnet-1.id
  nat       = true   # авто-выдача публичного IP
}
```

## Proxmox

`NAT` не является атрибутом сетевого устройства в proxmox-провайдере.

Подход:
- Внешний доступ обеспечивается на уровне моста/роутинга гипервизора (вне Terraform).
- Чтобы Terraform «видел» адрес гостевой ОС — включить QEMU agent:

```hcl
agent {
  enabled = true
}

network_device {
  bridge  = "vmbr0"
  enabled = true
}
```

## Решение

`network_device { bridge = "vmbr0" }` + `agent { enabled = true }`. Публичный IP и NAT
настраиваются на стороне гипервизора (iptables/маршрутизация на ноде PVE), а не ресурсом Terraform.