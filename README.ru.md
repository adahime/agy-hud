<div align="center">

<img src="docs/assets/banner.svg" alt="Баннер AGY-HUD" width="100%" />

<p>
  <strong>Монитор скорости генерации, TTFT, фактического маршрутизированного ID модели и заполнения контекста для Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Лицензия: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Стандартная библиотека Python 3.9+" />
  <img src="https://img.shields.io/badge/Node.js-22.5%2B%20node%3Asqlite-06b6d4?style=flat-square" alt="Node.js 22.5+ node:sqlite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20External-10b981?style=flat-square" alt="Без внешних пакетов" />
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

**AGY-HUD** — это легкий плавающий виджет для рабочего стола, консольная утилита и плагин боковой панели для Google Antigravity. Программа открывает локальные базы данных SQLite (`~/.gemini/antigravity/conversations/<uuid>.db` и `-wal`) строго в режиме только для чтения и показывает скорость генерации токенов, время до первого токена (`TTFT`), **фактический идентификатор модели, на которую был маршрутизирован запрос**, и заполнение контекстного окна без перехвата сетевого трафика.

### Основные возможности

- **Приоритет фактического ID маршрутизированной модели**: В первую очередь считывает поле protobuf `f19` — фактический идентификатор модели на бэкенде (например, `gemini-3.8-flash-k`), а не отображаемое в интерфейсе название (`f21`, используемое только если `f19` отсутствует). Также считывает фактический лимит контекста из `f9.f10.f4` (например, `256,000`).
- **Скорость генерации и общая скорость**: Вычисляет как скорость потокового вывода после первого токена (`GEN TPS = вывод / время_потока`), так и общую скорость с учетом начального ожидания (`E2E TPS = вывод / (TTFT + время_потока)`). Ответы длительностью менее `0.5s` (или менее `1.0s` со скоростью выше `1,200 tok/s`) помечаются как `BUF`, исключаются из `PEAK TPS` и отображаются через `E2E` и предыдущую устойчивую скорость потока (`STR`).
- **Локальное чтение без записи**: Настольное окно и CLI на Python подключаются через SQLite URI `?mode=ro` и отслеживают время изменения `.db` и `.db-wal`; плагин боковой панели использует встроенный в Node.js модуль `node:sqlite` с флагом `{ readOnly: true }`. Ключи API и настройка прокси не требуются.
- **Без внешних пакетов**: Настольное окно и CLI используют только стандартную библиотеку Python 3.9+ (`sqlite3`, `tkinter`), а плагин боковой панели работает на встроенном в Antigravity `sidecar_sdk` и `node:sqlite` из Node.js 22.5+. Установка через `pip install` или `npm install` не требуется.
- **Плавающее окно, CLI и боковая панель**: Боковая панель автоматически подстраивается под светлую или темную тему IDE, позволяет переключаться между `Auto Pane`, `Latest DB` или 15 последними диалогами и строит диаграмму по 28 последним вызовам плюс журнал на 30 записей. По умолчанию используются краткие английские обозначения (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) с переключением между `EN` и `中文`.

---

## <a id="quick-start"></a>Быстрый старт

### 1. Плагин боковой панели Antigravity 2.0

Устанавливается в `~/.gemini/config/plugins/agy-hud` (перезагрузите или перезапустите Antigravity, если значок не появился сразу):

```bash
python plugin/install_plugin.py
```

Удаление плагина:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Автономное настольное окно и CLI

Работает полностью независимо и не меняет настройки существующих плагинов Antigravity:

- **Windows (без окна консоли)**: дважды щелкните `desktop/launch.bat` или `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Запустить плавающее окно (по умолчанию: EN, обновление 500 мс, прозрачность 92%)
python -m desktop.cli

# Дополнительные флаги: --lang en|zh, --refresh-ms 500, --alpha 0.92
python -m desktop.cli --lang zh --refresh-ms 1000

# Вывести один снимок в терминал и выйти
python -m desktop.cli --cli

# Выводить строку сводки при завершении каждого нового ответа (--interval по умолчанию 1.0 с)
python -m desktop.cli --watch --interval 1.0
```

> [!TIP]
> Перетаскивайте окно левой кнопкой за верхнюю панель (если позиция не закреплена), нажимайте `▾` или дважды щелкайте по тексту для раскрытия/скрытия карточки и нажмите **правой кнопкой мыши** в любом месте окна, чтобы изменить **Язык (`EN` / `中文`)**, **Поверх всех окон**, **Закрепить позицию**, **Прозрачность (`100%`–`50%`)** или **Интервал обновления (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Поля данных

AGY-HUD считывает таблицы `gen_metadata` и `steps` из `~/.gemini/antigravity/conversations/<uuid>.db`:

| Путь поля | Извлекаемые данные | Резервный вариант |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | **Фактический ID маршрутизированной модели** (напр. `gemini-3.8-flash-k`) | Отображаемое в UI имя (`f1.f21`) |
| `gen_metadata.f1.f4` | Кэш (`f5`), новый ввод (`f2`), вывод (`f3` или `f1`), размышления (`f9`), видимый текст (`f10`) | Устаревший формат (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Текущий объем контекста (`f1`) и лимит окна (`f4`, напр. `256,000`) | `кэш + новый ввод`; таблица лимитов моделей |
| `gen_metadata.f1.f11` / `f1.f12` | Время до первого токена (`TTFT`, `f11`) и длительность потоковой генерации (`f12`) | `0.0s` |
| `steps` (`status != 3`) | Время выполняемого шага генерации (`step_type = 15`); плагин также отображает `TOOL` на прочих активных шагах и берет время вызовов через `f1.f20` | Состояние ожидания |

---

## Структура проекта

```text
agy-hud/
├── desktop/                     # Плавающее окно и CLI на стандартной библиотеке Python 3.9+
│   ├── telemetry.py             # Чтение SQLite (?mode=ro) + WAL и разбор protobuf
│   ├── hud_pill.py              # Безрамочное окно Tkinter, карточка и интерфейс EN/中文
│   ├── cli.py                   # Точка входа для GUI / --cli / --watch
│   ├── launch.pyw               # Фоновый запуск для Windows без консоли
│   └── launch.bat               # Пакетный запуск для Windows двойным щелчком
├── plugin/                      # Плагин боковой панели Antigravity 2.0
│   ├── plugin.json              # Манифест плагина
│   ├── install_plugin.py        # Скрипт установки и удаления
│   ├── assets/logo.svg          # Иконка плагина
│   └── sidecars/hud_panel/      # Бэкенд node:sqlite (опрос 450 мс, ETag) и веб-панель
├── docs/
│   └── assets/                  # SVG-баннер и изображения предпросмотра
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Лицензия

Распространяется под лицензией [MIT License](LICENSE).
