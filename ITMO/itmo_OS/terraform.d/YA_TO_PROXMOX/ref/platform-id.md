# Подход: `platform_id` в Yandex → Proxmox

## Yandex

```hcl
resources {
  platform_id = "standard-v2"   # или high-cpu, gpu-standard-v1 ...
}
```

## Proxmox

Семейств платформ `standard-*` / `high-cpu` / `gpu-*` нет.

Подход:
- `cpu { type = "..." }` — эмулируемый тип CPU (рекомендовано `x86-64-v2-AES` и выше).
- GPU-семейства yandex (`gpu-standard-v1`) → в proxmox через проброс устройств:
  ```hcl
  hostpci {
    device = "hostpci0"
    id     = "0000:01:00.0"
  }
  ```
  либо через resource mapping.

```hcl
cpu {
  cores   = 1
  sockets = 1
  type    = "x86-64-v2-AES"
}
```

## Решение

Готовые платформы yandex не переносятся 1:1. Подобрать `cpu.type` под нужные возможности;
GPU — через `hostpci` / mapping.