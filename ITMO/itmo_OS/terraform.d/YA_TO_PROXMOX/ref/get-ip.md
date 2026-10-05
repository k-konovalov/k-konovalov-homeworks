# Подход: получение IP адреса VM в Yandex → Proxmox

## Yandex

```hcl
output "vm_ip" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}
```

## Proxmox

Адреса доступны через computed-атрибуты QEMU agent ресурса VM:

```hcl
resource "proxmox_virtual_environment_vm" "vm-1" {
  # ...
  agent { enabled = true }
}

output "vm_ip" {
  value = proxmox_virtual_environment_vm.vm-1.ipv4_addresses[0]
}
```

Доступные computed-атрибуты: `ipv4_addresses`, `ipv6_addresses`, `mac_addresses`,
`network_interface_names`.

## Решение

Требуется `agent { enabled = true }` и установленный QEMU guest agent в гостевой ОС.
Читать `ipv4_addresses` / `ipv6_addresses` из ресурса VM.