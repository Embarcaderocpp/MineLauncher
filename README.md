# MineLauncher

Неофициальный Minecraft Launcher с поддержкой популярных модлоадеров.

## Возможности

- Поддержка Vanilla, **Fabric**, **Forge**, **Quilt** и **NeoForge**
- Удобный графический интерфейс (CustomTkinter)
- Полноценный CLI через [Typer](https://typer.tiangolo.com/)
- Автоматический поиск Java 21+
- Прогресс установки с логами в реальном времени
- Настройка RAM и JVM-аргументов для каждого инстанса
- Кросс-платформенность (Windows / Linux / macOS)

## Требования

- Python 3.10+
- **Java 21+** (лаунчер пытается найти её автоматически)

## Установка

```bash
git clone https://github.com/yourname/MineLauncher.git
cd MineLauncher

# Создаём виртуальное окружение
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

Или с использованием `pyproject.toml`:

```bash
pip install -e .
```

## Запуск

### Графический интерфейс

```bash
# Через главный файл
python main.py --gui

# Если установили пакет
mc-launcher --gui
```

### Командная строка (CLI)

```bash
# Помощь
mc-launcher --help

# Создать инстанс
mc-launcher create my-world --version 1.21.5 --loader fabric

# Создать с конкретной версией модлоадера
mc-launcher create modded --loader forge --loader-version 47.3.0

# Запустить инстанс
mc-launcher launch my-world

# Список инстансов
mc-launcher list

# Доступные версии Minecraft
mc-launcher list-versions

# Информация об инстансе
mc-launcher info my-world

# Удалить инстанс
mc-launcher delete my-world
```

## Структура проекта

```
MineLauncher/
├── main.py                 # Точка входа (GUI + CLI)
├── mc_launcher/
│   ├── cli/                # Команды командной строки
│   ├── core/               # Логика установки и запуска
│   │   ├── installer.py
│   │   ├── manager.py
│   │   └── runner.py
│   ├── gui/                # Графический интерфейс
│   ├── config.py           # Настройки + поиск Java
│   └── models.py
├── instances/              # Ваши игровые инстансы (не в репозитории)
└── requirements.txt
```

## Разработка

```bash
pip install -e ".[dev]"
ruff check .
```

## Лицензия

MIT

---

**Примечание:** Это неофициальный лаунчер. Используйте на свой страх и риск.
