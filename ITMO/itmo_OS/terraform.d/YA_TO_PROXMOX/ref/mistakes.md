# Типичные ошибки при переносе: Yandex → Proxmox

1. Забыть `node_name` (обязателен в proxmox).
2. Перепутать единицы памяти (ГБ vs МиБ).
3. Указывать `subnet_id` (нет в proxmox) вместо `bridge`.
4. Оставлять IAM-токен/`cloud_id`/`folder_id` из yandex в провайдере proxmox.
5. Не включать `agent { enabled = true }` там, где нужны IP из гостевой ОС (аналог публичных IP yandex).