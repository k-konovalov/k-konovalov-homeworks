# Подход: загрузка из образа/шаблона в Yandex → Proxmox

## Yandex

```hcl
boot_disk {
  initialize_params {
    image_id = yandex_compute_image.my-img.id
  }
}
```

## Proxmox

Два основных варианта.

### Вариант A — свежий пустой диск

```hcl
disk {
  interface    = "scsi0"
  datastore_id = "local-lvm"
  size         = 20
}
```

### Вариант B — из образа/шаблона

1. Скачать cloud-образ в хранилище:
   ```hcl
   resource "proxmox_virtual_environment_download_file" "debian" {
     content_type = "iso"          # или "import" / "vztmpl"
     datastore_id = "local"
     node_name    = "pve"
     url          = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2"
   }
   ```
   либо `proxmox_virtual_environment_file` для загрузки локального файла.

2. Клонировать из готового шаблона VM:
   ```hcl
   clone {
     vm_id       = 9000            # ID шаблона
     datastore_id = "local-lvm"
     full        = true
   }
   ```

## Решение

Для свежей VM без ОС — пустой диск (`disk`). Для запуска с ОС — скачивание образа
(`proxmox_virtual_environment_download_file`) или клонирование шаблона (`clone`).