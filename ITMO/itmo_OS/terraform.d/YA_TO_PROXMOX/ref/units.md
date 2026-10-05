# Единицы измерения: Yandex → Proxmox

- **Память**: Yandex `resources.memory` в **ГБ**, Proxmox `memory.dedicated` в **МиБ** → умножать на 1024.
- **Диск**: Yandex `size` в **ГБ**, Proxmox `disk.size` в **number** (ГиБ) → без пересчёта.
- **Скорость/лимиты**: Yandex `core_fraction` (проценты) → Proxmox `cpu.limit` (0 = без лимита).