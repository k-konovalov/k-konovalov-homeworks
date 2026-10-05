# Провайдер (provider): Yandex → Proxmox

## Yandex (`yandex`)

```hcl
provider "yandex" {
  token     = "..."        # или service_account_key_file
  cloud_id  = "..."
  folder_id = "..."
  zone      = "ru-central1-d"
}
```

Ключевые атрибуты провайдера yandex (по [overview](https://yandex.cloud/ru/docs/terraform/tf-ref/overview)):
`cloud_id`, `folder_id`, `zone`, `token` / `service_account_key_file`, `endpoint`, `max_retries`,
`organization_id`, `region_id`, `storage_*`, `ymq_*`, `yq_endpoint`, `insecure`, `plaintext`, `profile`.

## Proxmox (`bpg/proxmox`)

```hcl
provider "proxmox" {
  endpoint  = "https://10.0.0.2:8006/"
  username  = "root@pam"
  password  = "..."         # или api_token
  insecure  = true          # self-signed TLS
}
```

Ключевые атрибуты провайдера proxmox (из `bpg.proxmox.scheme.json`, блок `provider`):
`endpoint`, `username`, `password`, `api_token`, `insecure`, `min_tls`, `api_headers`,
`auth_ticket`, `csrf_prevention_token`, `otp` (deprecated), `random_vm_id_start/end`, `random_vm_ids`, `tmp_dir`.
Блок `ssh`: `agent`, `agent_socket`, `username`, `password`, `private_key`, `socks5_*`, `node_address_source`.

## Таблица соответствия провайдеров

| Yandex | Proxmox | Комментарий |
|---|---|---|
| `token` / `service_account_key_file` | `username` + `password`, либо `api_token` | токен IAM не переносится; у proxmox 3 способа: API token, auth ticket, username/password |
| `cloud_id` + `folder_id` | — (не нужен) | proxmox не имеет иерархии облако/папка |
| `zone` (напр. `ru-central1-d`) | `node_name` на уровне ресурса | зона не задаётся в провайдере; нода указывается в каждом VM-ресурсе |
| `endpoint` | `endpoint` | одноимённо |
| `insecure` | `insecure` | одноимённо |