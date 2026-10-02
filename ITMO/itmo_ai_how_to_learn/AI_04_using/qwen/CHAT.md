# Terraform плагины из локальной папки

## 00. Запрос пользователя

как настроить подгрузку плагинов в terraform из локальной папки. приведи пример правильной структуры директории и настройки конфигов filesystem_mirror

## 01. Ответ ИИ

Настройка локального зеркала (filesystem mirror) для плагинов (провайдеров) Terraform чаще всего используется в изолированных контурах (air-gapped environments), в корпоративных CI/CD пайплайнах или для кэширования провайдеров.

Чтобы Terraform успешно подхватила плагин из локальной папки, необходимо строго соблюсти **структуру директорий** и правильно настроить **CLI-конфигурацию**.

Ниже приведена подробная инструкция.

---

### 1. Правильная структура директорий

Terraform ожидает, что локальное зеркало будет повторять структуру официального Terraform Registry. 
Путь к бинарному файлу должен выглядеть так:
`<путь_к_зеркалу>/<hostname>/<namespace>/<provider_name>/<version>/<os>_<arch>/terraform-provider-<name>_v<version>`

**Пример структуры для провайдера `hashicorp/aws` версии `5.50.0` под Linux (amd64):**

```text
/opt/terraform-mirror/               <-- Это будет ваш "path" в конфиге
└── registry.terraform.io/           <-- Имя реестра (hostname)
    └── hashicorp/                   <-- Namespace (автор)
        └── aws/                     <-- Имя провайдера
            └── 5.50.0/              <-- Версия провайдера
                └── linux_amd64/     <-- ОС и архитектура (darwin_amd64, windows_amd64 и т.д.)
                    └── terraform-provider-aws_v5.50.0  <-- Сам бинарный файл
```

*Важные правила именования:*
* Имя бинарного файла **обязательно** должно начинаться с `terraform-provider-` и содержать версию через `_v` (например, `terraform-provider-aws_v5.50.0`).
* В Linux/macOS файл должен иметь **права на исполнение** (`chmod +x terraform-provider-aws_v5.50.0`).
* Если вы используете кастомный реестр (например, `mycompany.com`), структура будет начинаться с `mycompany.com/...`.

---

### 2. Настройка CLI-конфигурации (`.terraformrc` или `terraform.rc`)

Terraform нужно сказать, где искать это зеркало. Для этого используется файл конфигурации CLI.

* **Linux / macOS:** `~/.terraformrc`
* **Windows:** `%APPDATA%\terraform.rc`

Откройте (или создайте) этот файл и добавьте блок `provider_installation`:

```hcl
provider_installation {
  # Указываем локальное зеркало
  filesystem_mirror {
    # Путь до корневой папки вашего зеркала (без registry.terraform.io в конце!)
    path = "/opt/terraform-mirror"
    
    # Опционально: можно указать, для каких именно реестров/провайдеров использовать зеркало
    include = ["registry.terraform.io/*/*"] 
    # include = ["registry.terraform.io/hashicorp/*"] # Только для hashicorp
  }

  # Опционально: указываем, что для остальных провайдеров можно ходить в интернет
  direct {
    exclude = ["registry.terraform.io/hashicorp/*"]
  }
}
```

*Если вы работаете в полностью изолированном контуре, блок `direct` можно опустить или настроить так, чтобы он исключал всё.*

---

### 3. Настройка конфигурации Terraform (`main.tf`)

В самом коде Terraform (`main.tf`) вы описываете провайдер как обычно. Убедитесь, что `source` и `version` **строго совпадают** с тем, что лежит в вашей локальной папке.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws" # Должно совпадать с <hostname>/<namespace>/<type>
      version = "5.50.0"        # Должно совпадать с папкой версии
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
```

---

### 4. Инициализация и проверка

Выполните команду инициализации:

```bash
terraform init
```

**Как понять, что всё получилось?**
В выводе `terraform init` вы должны увидеть сообщение, что провайдер установлен из локального источника, а не скачан из интернета:

```text
Initializing provider plugins...
- Finding hashicorp/aws versions matching "5.50.0"...
- Installing hashicorp/aws v5.50.0...
- Installed hashicorp/aws v5.50.0 (from local mirror /opt/terraform-mirror/registry.terraform.io/hashicorp/aws/5.50.0/linux_amd64)

Terraform has been successfully initialized!
```

---

### ⚠️ Частые ошибки и нюансы

1. **`Error: Failed to install provider` / `no matching versions`**
   * **Причина:** Terraform не нашла папку с версией или бинарник.
   * **Решение:** Проверьте, что имя файла точно `terraform-provider-<name>_v<version>` (без расширений вроде `.exe` для Linux, но с `.exe` для Windows). Проверьте права на файл (`ls -l`).
2. **Несоответствие архитектуры (`os_arch`)**
   * **Причина:** Вы скачали провайдер под `linux_amd64`, а запускаете Terraform на Mac с процессором Apple Silicon (`darwin_arm64`).
   * **Решение:** В папке версии должна лежать подпапка, точно соответствующая вашей ОС и архитектуре (`uname -m` и `uname -s` в Linux/Mac).
3. **Кэширование `.terraform`**
   * Если вы меняли структуру папок или `.terraformrc`, но Terraform упорно продолжает использовать старый провайдер, удалите папку `.terraform` и файл `.terraform.lock.hcl` в вашем проекте и запустите `terraform init` заново.

---

### 💡 P.S. А если вы разрабатываете свой собственный провайдер?
Если вам нужно не просто кэшировать готовые плагины, а **тестировать свой собственный провайдер**, который вы только что скомпилировали из исходников, используйте не `filesystem_mirror`, а **`dev_overrides`**.

В `.terraformrc`:
```hcl
provider_installation {
  dev_overrides {
    "mycompany/mycloud" = "/path/to/your/compiled/binary/directory"
  }
  direct {}
}
```
В этом случае структура папок не нужна, достаточно просто положить скомпилированный бинарник `terraform-provider-mycloud` в указанную директорию, и Terraform будет брать его напрямую, игнорируя версии и реестры (удобно для локальной разработки).

## 02. Запрос пользователя

напиши команду для mkdir -p для registry.terraform.io/bpg/proxmox и файла terraform-provider-proxmox_0.114.0_freebsd_amd64

## 03. Ответ ИИ

Вот команда для создания нужной структуры директорий:

```bash
mkdir -p registry.terraform.io/bpg/proxmox/0.114.0/freebsd_amd64
```

### ⚠️ Важное замечание по имени файла

Terraform **очень строго** относится к именованию бинарных файлов провайдеров. В имени файла **обязательно** должна присутствовать буква `v` перед номером версии. 

Если ваш файл сейчас называется `terraform-provider-proxmox_0.114.0_freebsd_amd64`, Terraform его **не увидит**. Правильный формат: `terraform-provider-proxmox_v0.114.0_freebsd_amd64`.

### Полный набор команд для подготовки

Если файл находится в текущей директории, выполните следующие команды:

```bash
# 1. Создаем структуру папок
mkdir -p registry.terraform.io/bpg/proxmox/0.114.0/freebsd_amd64

# 2. Переименовываем файл, добавляя букву "v" перед версией (если ее нет)
mv terraform-provider-proxmox_0.114.0_freebsd_amd64 terraform-provider-proxmox_v0.114.0_freebsd_amd64

# 3. Перемещаем файл в целевую директорию
mv terraform-provider-proxmox_v0.114.0_freebsd_amd64 registry.terraform.io/bpg/proxmox/0.114.0/freebsd_amd64/

# 4. Делаем файл исполняемым (обязательно для Linux/FreeBSD/macOS)
chmod +x registry.terraform.io/bpg/proxmox/0.114.0/freebsd_amd64/terraform-provider-proxmox_v0.114.0_freebsd_amd64
```

### Итоговая структура, которая получится:
```text
registry.terraform.io/
└── bpg/
    └── proxmox/
        └── 0.114.0/
            └── freebsd_amd64/
                └── terraform-provider-proxmox_v0.114.0_freebsd_amd64  <-- Исполняемый файл
```

После этого убедитесь, что в вашем `~/.terraformrc` путь `path` указывает на директорию, **в которой лежит папка** `registry.terraform.io` (то есть на родительскую папку), а не на саму папку `registry.terraform.io`.

## 04. Запрос пользователя

а приведи пример для dev_overrides

## 05. Ответ ИИ

Конфигурация **`dev_overrides`** — это специальный режим Terraform, предназначенный **исключительно для локальной разработки** собственных провайдеров. 

Его главное отличие от `filesystem_mirror` в том, что он **полностью игнорирует версии, архитектуру и ОС**. Terraform просто берет исполняемый файл из указанной папки, независимо от того, что написано в `required_providers`.

Ниже приведен полный пошаговый пример.

---

### Шаг 1: Подготовка бинарного файла

При использовании `dev_overrides` имя файла должно быть максимально простым: `terraform-provider-<имя_провайдера>`. Суффиксы версии и архитектуры (`_v1.0.0_linux_amd64`) **не нужны** и могут даже помешать.

Допустим, вы разрабатываете провайдер с именем `mycloud`. Скомпилируйте его в специальную папку (например, `~/.terraform.d/plugins`):

```bash
# Переходим в исходный код вашего провайдера
cd ~/projects/terraform-provider-mycloud

# Собираем бинарник с простым именем в целевую папку
go build -o ~/.terraform.d/plugins/terraform-provider-mycloud
```
*(Убедитесь, что файл имеет права на исполнение: `chmod +x ~/.terraform.d/plugins/terraform-provider-mycloud`)*

---

### Шаг 2: Настройка `~/.terraformrc`

Откройте файл конфигурации CLI Terraform (`~/.terraformrc` на Linux/macOS или `%APPDATA%\terraform.rc` на Windows) и добавьте следующий блок:

```hcl
provider_installation {
  # Указываем прямую ссылку на папку с бинарником
  dev_overrides {
    # Ключ должен точно совпадать с "source" в вашем main.tf
    "mycompany/mycloud" = "/home/user/.terraform.d/plugins"
  }

  # Для всех остальных провайдеров используем стандартный реестр
  direct {}
}
```
*Обратите внимание: путь указывает на **папку**, в которой лежит файл `terraform-provider-mycloud`, а не на сам файл.*

---

### Шаг 3: Конфигурация проекта (`main.tf`)

В вашем Terraform-коде укажите провайдер как обычно. 

⚠️ **Важно:** Атрибут `version` в блоке `required_providers` будет **проигнорирован**, но указать его всё равно рекомендуется для документирования. Главное, чтобы `source` точно совпадал с ключом в `dev_overrides`.

```hcl
terraform {
  required_providers {
    mycloud = {
      source  = "mycompany/mycloud" # Должно совпадать с ключом в dev_overrides
      version = "9.9.9"             # Будет проигнорировано при наличии dev_overrides
    }
  }
}

provider "mycloud" {
  # Ваши настройки провайдера
  api_token = "test-token"
}

resource "mycloud_server" "example" {
  name = "dev-test-server"
}
```

---

### Шаг 4: Инициализация и проверка

Запустите инициализацию в папке с `main.tf`:

```bash
terraform init
```

**Ожидаемый вывод:**
Terraform намеренно выдаст **яркое предупреждение**, чтобы вы не забыли, что используете режим разработки. Это нормально!

```text
╷
│ Warning: Provider development overrides are in effect
│ 
│ The following provider development overrides are set in the CLI configuration:
│  - mycompany/mycloud in /home/user/.terraform.d/plugins
│ 
│ The behavior may therefore not match any released version of the provider and 
│ applying changes may cause the state to become incompatible with published releases.
╵

Initializing the backend...
Initializing provider plugins...
- Finding mycompany/mycloud versions matching "9.9.9"...
- Installing mycompany/mycloud v9.9.9...
- Installed mycompany/mycloud v9.9.9 (unauthenticated)

Terraform has been successfully initialized!
```

Обратите внимание на строку: `Installed mycompany/mycloud v9.9.9 (unauthenticated)`. Terraform "притворяется", что установил версию 9.9.9, но на самом деле использует ваш локальный бинарник.

---

### ⚠️ Критически важные правила для `dev_overrides`

1. **Только для локальной разработки**: Никогда не используйте `dev_overrides` в CI/CD (GitLab CI, GitHub Actions) или на продакшене. Для этих целей используйте `filesystem_mirror` или внутренний артефакт-репозиторий (Artifactory/Nexus).
2. **Имя файла**: Бинарник должен называться строго `terraform-provider-<имя>` (например, `terraform-provider-proxmox`). Если вы назовете его `terraform-provider-proxmox_v0.114.0`, Terraform его не найдет в режиме `dev_overrides`.
3. **Очистка**: Когда вы закончите разработку, **обязательно удалите** блок `dev_overrides` из `~/.terraformrc`. Если забыть это сделать, вы можете потратить часы на отладку, пытаясь понять, почему Terraform не скачивает новую версию провайдера из реестра.
4. **Очистка кэша**: Если вы пересобрали провайдер, а Terraform использует старую логику, удалите папку `.terraform` в проекте и выполните `terraform init` заново.
