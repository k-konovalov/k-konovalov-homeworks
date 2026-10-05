---
name: yandex-to-proxmox
description: Маппинг схемы провайдера Yandex Cloud (yandex) на схему провайдера Proxmox VE (bpg/proxmox). Используется при переносе Terraform-конфигов с Yandex Cloud на Proxmox VE.
---

# Маппинг схем Yandex Cloud → Proxmox VE

Этот SKILL описывает соответствие между ресурсами/атрибутами провайдера **Yandex Cloud** (`yandex/*`)
и провайдера **Proxmox VE** (`bpg/proxmox`). Применяется при переписывании Terraform-конфигов.

## Проверка применимости

Применяется, когда нужно переписать/перенести конфиг для провайдера `yandex` в эквивалент для
`bpg/proxmox` (Proxmox VE). Скилл активируется по одному из ключевых слов/фраз ниже.

### Ключевые слова (триггеры)

**Переход Yandex → Proxmox (RU):**
«перепиши с yandex на proxmox», «переведи yandex в proxmox», «перенеси yandex на proxmox»,
«конвертируй конфиг yandex в proxmox», «переделай yandex под proxmox», «адаптируй yandex для proxmox»,
«замени yandex-провайдер на proxmox».

**То же (EN):**
«rewrite yandex to proxmox», «translate yandex to proxmox», «port yandex to proxmox»,
«convert yandex to proxmox», «migrate terraform provider from yandex to proxmox»,
«move yandex resources to proxmox», «swap yandex provider for proxmox».

**Terraform/провайдеры:**
«terraform yandex proxmox», «yandex provider proxmox», «bpg/proxmox», «proxmox provider»,
«перенос terraform-конфига», «terraform migration yandex proxmox», «у меня конфиг yandex, нужен proxmox».

**Ресурсы/типовые конструкции (встречается yandex_* или его proxmox-аналог):**
`yandex_compute_instance`, `yandex_compute_disk`, `yandex_vpc_subnet`, `yandex_vpc_network`,
`proxmox_virtual_environment_vm`, `proxmox_virtual_environment_download_file`,
упоминание `resources.cores/memory`, `boot_disk`, `network_interface`, `core_fraction`.

Если запрос содержит комбинацию «yandex» + «proxmox» (или их ресурсов) и желание перенести/переписать —
скилл применим.

## Структура пакета

| Файл | Содержание |
|---|---|
| [`SKILL.md`](SKILL.md) | этот индекс + инструкция по пополнению маппинга |
| [`map.json`](map.json) | машиночитаемый маппинг команд: `{ yandex_command, proxmox_command, description, reference }` |
| [`ref/provider.md`](ref/provider.md) | конфигурация и атрибуты провайдеров (yandex vs proxmox) |
| [`ref/resources.md`](ref/resources.md) | маппинг ресурсов (`yandex_compute_instance`, диски, сеть и др.) |
| [`ref/units.md`](ref/units.md) | единицы измерения (ГБ vs МиБ и т.п.) |
| [`ref/mistakes.md`](ref/mistakes.md) | типичные ошибки при переносе |
| `ref/<approach>.md` | фрагменты по отдельным подходам без прямого аналога (см. [`map.json`](map.json) `reference`) |

## Справочный материал

Подробности вынесены в отдельные файлы каталога [`ref/`](ref/):

- **[Провайдер (provider)**](ref/provider.md) — блок `provider`, атрибуты и таблица соответствия.
- **[Ресурсы (resource_schemas)**](ref/resources.md) — `yandex_compute_instance` → `proxmox_virtual_environment_vm`,
  диски, сеть, прочие ресурсы proxmox.
- **[Единицы измерения**](ref/units.md) — пересчёт ГБ/МиБ/лимитов.
- **[Типичные ошибки при переносе**](ref/mistakes.md) — чек-лист частых проблем.

### Документация и получение схем провайдеров

| Провайдер | Документация | Как получить схему |
|---|---|---|
| Yandex Cloud (`yandex/*`) | [Overview](https://yandex.cloud/ru/docs/terraform/tf-ref/overview) (список ресурсов — в навигации слева) | команда ниже; локального JSON нет |
| Proxmox VE (`bpg/proxmox`) | [Index](https://github.com/bpg/terraform-provider-proxmox/blob/main/docs/index.md) | локальный файл [`proxmox-provider.docs/bpg.proxmox.scheme.json`](../../proxmox-provider.docs/bpg.proxmox.scheme.json) или команда ниже |

**Универсальная команда получения JSON-схемы всех настроенных провайдеров** (требует `terraform init` в каталоге с конфигом):

```sh
terraform providers schema -json > providers-schema.json
```

Файл `providers-schema.json` содержит `provider_schemas.<registry>/<name>/provider.block` (атрибуты провайдера)
и `resource_schemas` (все ресурсы с полями `required`/`optional`/`computed`, блоками и вложенными атрибутами).
Из него удобно брать актуальные имена ресурсов/атрибутов при пополнении [`map.json`](map.json).

> Локальный файл схемы proxmox уже лежит в репозитории:
> [`proxmox-provider.docs/bpg.proxmox.scheme.json`](../../proxmox-provider.docs/bpg.proxmox.scheme.json).
> Схема yandex в репозитории отсутствует — брать из документации или из `terraform providers schema -json`
> при подключённом `yandex`-провайдере.

## Как пополнять маппинг новыми командами

Если в мигрируемом конфиге встречается новая конструкция yandex, которой ещё нет
в [`map.json`](map.json), `ref/*.md` или справочнике — действовать по инструкции ниже.

### Алгоритм

1. **Найди yandex-конструкцию.** Определи ресурс/атрибут/блок (например `yandex_compute_disk`,
   `network_interface.nat_ip_address`, новый `yandex_lb_*`, и т.п.) и убедись, что его нет в `map.json`.
2. **Определи, есть ли прямой аналог в proxmox.**
   - **Есть прямой аналог** → добавь запись только в `map.json` (см. формат записи), поле `reference` не нужно.
   - **Прямого аналога нет / аналог нетривиален** → создай новый фрагмент-файл в `ref/` (один файл = один
     подход) и сошлись на него из записи `map.json` через поле `reference`.
3. **Обнови справочник** ([`ref/resources.md`](ref/resources.md), [`ref/units.md`](ref/units.md) и т.п.),
   если новая команда расширяет уже описанную область, чтобы документация оставалась актуальной.
4. **Валидируй JSON** (см. раздел «Валидация»).

### Формат записи в `map.json`

Массив `mapping` в `map.json` содержит объекты:

```json
{
  "yandex_command": "уникальная конструкция/команда yandex (как в .tf)",
  "proxmox_command": "эквивалентная конструкция proxmox (или пустая строка \"\")",
  "description": "краткое пояснение (единицы, нюансы, предупреждения)",
  "reference": "ref/<file>.md"
}
```

- Поля `yandex_command`, `proxmox_command`, `description` обязательны.
- Поле `reference` — **только** если нет прямого аналога; указывает путь к фрагменту в `ref/`
  относительно `YA_TO_PROXMOX/` (например `ref/nat.md`).
- `proxmox_command` может быть `""` с пояснением в `description`, когда эквивалента нет вовсе.

### Создание фрагмента-подхода в `ref/`

Когда прямого 1:1 соответствия нет, создай отдельный `.md`-файл в папке `ref/` по правилам:

- **Один файл = один подход/случай.** Имя файла — краткое kebab-case описание (например `load-balancer.md`).
- Шаблон содержимого:

    ```markdown
    # Подход: <что маппится> в Yandex → Proxmox

    ## Yandex

    <исходная yandex-конструкция в hcl-коде>

    ## Proxmox

    <вариант(ы) переноса с примерами>

    ## Решение

    <принятое решение / рекомендация>
    ```

- Внутри можно описать несколько вариантов (вариант A/B), но файл посвящён одному подходу.
- После создания — сослаться на него из записи `map.json` через `"reference": "ref/<file>.md"`.