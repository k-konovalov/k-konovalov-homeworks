# Ресурсы (resource_schemas): Yandex → Proxmox

Провайдер proxmox предоставляет большой набор ресурсов (`proxmox_*`). Ниже — маппинг ключевых ресурсов yandex.

## Compute instance: `yandex_compute_instance` → `proxmox_virtual_environment_vm`

Наиболее частый случай переноса. Основные атрибуты из схемы `proxmox_virtual_environment_vm`:

- Обязательные: `node_name` (string).
- Основные: `name`, `description`, `vm_id`, `started`, `on_boot`, `tags`, `template`, `machine`,
  `bios`, `acpi`, `scsi_hardware`, `hotplug`, `kvm_arguments`, `pool_id`, `protection`,
  `purge_on_destroy`, `stop_on_destroy`, `reboot`, `timeout_*`.
- Блоки: `cpu`, `memory`, `disk`, `network_device`, `agent`, `clone`, `cdrom`, `efi_disk`,
  `initialization` (cloud-init: `dns`, `ip_config`, `user_account`), `serial_device`, `smbios`,
  `startup`, `vga`, `tpm_state`, `usb`, `hostpci`, `virtiofs`, `watchdog`, `numa`, `rng`, `audio_device`, `amd_sev`.

| Yandex (`yandex_compute_instance`) | Proxmox (`proxmox_virtual_environment_vm`) | Комментарий |
|---|---|---|
| `name` | `name` | одноимённо |
| `resources.cores` | `cpu.cores` (+ `cpu.sockets`) | в yandex — «ядра»; в proxmox ядра на сокет + число сокетов |
| `resources.core_fraction` | `cpu.limit` / `cpu.units` | долевое выделение CPU (аналог лимита) |
| `resources.memory` (ГБ) | `memory.dedicated` (МиБ) | **единицы разные**: ГБ → МиБ ×1024 |
| `resources.gpus` | — | GPU-доступ в proxmox через `hostpci`/`mapping`, не напрямую |
| `boot_disk.disk_id` | `disk { interface, datastore_id, size }` | в proxmox диск описывается инлайн; интерфейс scsi0/virtio0/sata0/ide0 |
| `secondary_disk` | `disk` (несколько блоков, до 31) | список блоков `disk` |
| `network_interface.subnet_id` | `network_device.bridge` | в proxmox нет VPC-подсетей; сеть = мост (обычно `vmbr0`) |
| `network_interface.nat` | (мост + `agent.enabled`) | NAT не является прямым атрибутом; доступ даёт мост, IP читаются через QEMU agent |
| `network_interface.ipv4_address` (static) | `initialization.ip_config.ipv4.address` | статический IP задаётся в cloud-init |
| `network_interface.nat_ip_address` | `network_device.mac_address` / computed `ipv4_addresses` | публичный адрес из атрибутов QEMU agent |
| `zone` | `node_name` | нода, где создаётся VM |
| `platform_id` | `cpu.type` | эмуляция CPU (напр. `x86-64-v2-AES`) |
| `metadata` (user-data/ssh-keys) | `initialization` (cloud-init) | метаданные → cloud-init блок |
| `allow_stopping_for_update` | `reboot_after_update` | поведение при обновлении |

Пример эквивалента (yandex: 1 core, 2 ГБ, boot disk, сеть):

```hcl
resource "proxmox_virtual_environment_vm" "vm-1" {
  name      = "vm-1"
  node_name = "pve"

  started = true
  agent { enabled = true }

  cpu {
    cores   = 1
    sockets = 1
  }

  memory {
    dedicated = 2048   # 2 ГБ * 1024 = 2048 МиБ
  }

  disk {
    interface    = "scsi0"
    datastore_id = "local-lvm"
    size         = 20
  }

  network_device {
    bridge  = "vmbr0"
    enabled = true
  }
}
```

## Диски: `yandex_compute_disk` → часть блока `disk` ресурса VM

В proxmox отдельного ресурса «диск VM» нет: диск управляется внутри `proxmox_virtual_environment_vm`
через блок `disk`. Отдельно существуют `proxmox_virtual_environment_file` /
`proxmox_download_file` для загрузки образов/ISO в хранилище.

| Yandex (`yandex_compute_disk`) | Proxmox (`disk` блок) |
|---|---|
| `name` | `interface` (slot, напр. scsi0) |
| `size` (ГБ) | `size` (number, ГиБ) |
| `type` (network-hdd/ssd/nvme) | `datastore_id` + `file_format` + `ssd` | выбор хранилища/формата (raw/qcow2) |
| `image_id` | `file_id` / `import_from` / `clone` | источник образа |

## Сеть: `yandex_vpc_subnet` → мост (bridge)

В proxmox нет ресурса подсети. Аналог сети — мост на гипервизоре (`vmbr0`, `vmbr1`, ...), который
задаётся строкой в `network_device.bridge`. VLAN-тегирование — через `network_device.vlan_id` и `trunks`.

| Yandex (`yandex_vpc_subnet`) | Proxmox |
|---|---|
| `network_id` / `zone` | `bridge` (имя моста) |
| `v4_cidr_blocks` | `initialization.ip_config.ipv4.address` + `gateway` (cloud-init) |
| NAT (internet access) | мост + шлюз в cloud-init |

## Прочие полезные ресурсы proxmox

- `proxmox_download_file` — скачивание cloud-образов в хранилище
  (устаревшее имя `proxmox_virtual_environment_download_file` удалят в v1.0).
- `proxmox_virtual_environment_clone` — клонирование VM из шаблона.
- `proxmox_virtual_environment_container` — LXC-контейнеры (аналог лёгких VM).
- `proxmox_virtual_environment_pool` — пулы.
- `proxmox_virtual_environment_dns`, `proxmox_virtual_environment_user`, `proxmox_virtual_environment_role` — доступы.