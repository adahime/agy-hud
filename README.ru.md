<div align="center">

<img src="docs/assets/banner.svg" alt="Баннер AGY-HUD" width="100%" />

<p>
  <strong>Монитор скорости генерации, TTFT, активной модели и заполнения контекста для Google Antigravity в реальном времени</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Лицензия: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Стандартная библиотека Python 3.9+" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Встроенный SQLite в Node.js" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Без внешних зависимостей" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="Документация на 8 языках" />
</p>

<p>
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <strong>Русский</strong>
</p>

<p>
  <a href="#overview">Описание</a> ·
  <a href="#quick-start">Быстрый старт</a> ·
  <a href="#protobuf-map">Поля данных</a> ·
  <a href="CHANGELOG.md">История изменений</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="Предпросмотр плавающего окна и боковой панели AGY-HUD" width="100%" />
</div>

---

## <a id="overview"></a>Описание

**AGY-HUD** — это легкий плавающий виджет для рабочего стола, консольная утилита и плагин боковой панели для Google Antigravity. Программа открывает локальные базы данных SQLite в режиме только для чтения (`?mode=ro`) и показывает скорость генерации токенов, время до первого токена (`TTFT`), текущую модель и заполнение контекстного окна без перехвата сетевого трафика.

### Основные возможности

- **Чтение локальной базы без записи**: Читает `~/.gemini/antigravity/conversations/<uuid>.db` строго в режиме только для чтения (`?mode=ro`). Ключи API и настройка прокси не требуются.
- **Скорость генерации и общая скорость**: Показывает как скорость потокового вывода после первого токена (`GEN TPS = вывод / время_потока`), так и общую скорость с учетом начальной задержки (`E2E TPS = вывод / (TTFT + время_потока)`). Ответы, полученные быстрее 500 мс, отмечаются как `BUF`, чтобы короткие всплески не искажали статистику пиковой скорости.
- **Точное определение модели и лимита контекста**: Считывает идентификатор модели из поля `f19` (например, `gemini-3.8-flash-k`) и фактический лимит контекстного окна из `f9.f10.f4` (например, `256,000`).
- **Без внешних зависимостей**: Настольное окно и CLI используют только стандартную библиотеку Python (`sqlite3`, `tkinter`), а плагин боковой панели работает на встроенном модуле `node:sqlite`. Установка пакетов через `pip install` или `npm install` не требуется.
- **Переключение интерфейса EN / 中文**: По умолчанию используются краткие английские обозначения (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`), но в любой момент можно переключиться между английским и китайским через контекстное меню или кнопку в заголовке.

---

## <a id="quick-start"></a>Быстрый старт

### 1. Плагин боковой панели Antigravity 2.0

Устанавливается в `~/.gemini/config/plugins/agy-hud` для просмотра графиков TPS и истории последних запросов прямо в боковой панели (автоматически подстраивается под светлую и темную тему):

```bash
python plugin/install_plugin.py
```

Удаление плагина:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Автономное настольное окно и CLI

Работает полностью независимо и не меняет настройки существующих плагинов Antigravity:

- **Запуск на рабочем столе Windows (без окна консоли)**: дважды щелкните `desktop/launch.bat` или `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Запустить плавающее окно на рабочем столе (по умолчанию: английский, обновление каждые 500 мс)
python -m desktop.cli

# Вывести текущий снимок в терминал один раз
python -m desktop.cli --cli

# Непрерывно обновлять показатели в терминале
python -m desktop.cli --watch
```

> [!TIP]
> Нажмите **правой кнопкой мыши** в любом месте плавающего окна, чтобы изменить **Язык (`EN` / `中文`)**, **Поверх всех окон**, **Закрепить позицию**, **Прозрачность (`100%`–`50%`)** или **Интервал обновления (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Поля данных

AGY-HUD извлекает следующие данные из `~/.gemini/antigravity/conversations/<uuid>.db`:

| Путь поля | Показатель | Резервный вариант |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Определенный идентификатор модели (`gemini-3.8-flash-k`) | Отображаемое имя (`f1.f21`) |
| `gen_metadata.f1.f4` | Кэш (`f5`), новый ввод (`f2`), вывод (`f3`), размышления (`f9`), видимый текст (`f10`) | Устаревшие счетчики (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Текущий объем контекста (`f1`) и лимит окна (`f4`, напр. `256,000`) | Таблица лимитов моделей |
| `gen_metadata.f1.f11` / `f12` | Время до первого токена (`TTFT`) и длительность потокового вывода | `0.0s` |
| `steps` (последняя активная строка) | Прошедшее время выполняемого шага (`step_type = 15`) | Состояние ожидания |

---

## Структура проекта

```text
agy-hud/
├── desktop/                     # Настольное окно и CLI на стандартном Python
│   ├── telemetry.py             # Чтение SQLite + WAL и разбор protobuf
│   ├── hud_pill.py              # Плавающее окно Tkinter и подробная карточка
│   ├── cli.py                   # Точка входа для GUI / --cli / --watch
│   ├── launch.pyw               # Фоновый запуск для Windows без консоли
│   └── launch.bat               # Пакетный запуск для Windows двойным щелчком
├── plugin/                      # Плагин боковой панели Antigravity 2.0
│   ├── plugin.json              # Манифест плагина
│   ├── install_plugin.py        # Скрипт установки и удаления
│   ├── assets/logo.svg          # Иконка плагина
│   └── sidecars/hud_panel/      # Серверная часть на node:sqlite и веб-панель
├── docs/
│   └── assets/                  # SVG-баннер и изображения предпросмотра
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Лицензия

Распространяется под лицензией [MIT License](LICENSE).
