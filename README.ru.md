<div align="center">

<img src="docs/assets/banner.svg" alt="Баннер AGY-HUD" width="100%" />

<p>
  <strong>HUD в реальном времени для мониторинга Token/s, TTFT, сырого ID модели и контекстного окна в Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Лицензия: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Встроенный SQLite в Node.js" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Ноль зависимостей" />
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
  <a href="#overview">Обзор</a> ·
  <a href="#quick-start">Быстрый старт</a> ·
  <a href="#protobuf-map">Карта Protobuf</a> ·
  <a href="CHANGELOG.md">История изменений</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="Предпросмотр плавающей панели и боковой панели AGY-HUD" width="100%" />
</div>

---

## <a id="overview"></a>Почему AGY-HUD?

Большинство счетчиков токенов проксируют ваш API-трафик или оценивают объем клиентскими токенизаторами. **AGY-HUD** напрямую подключается к локальным базам данных диалогов SQLite + WAL в Google Antigravity в строгом режиме только для чтения (`?mode=ro`) и декодирует бинарные protobuf-записи `gen_metadata` и `steps` прямо с диска.

| Возможности | Подробности |
| :--- | :--- |
| **Двойная метрика TPS** | Измеряет как чистую скорость потоковой генерации (`GEN TPS = output / stream_sec`), так и ощущаемую сквозную скорость (`E2E TPS = output / (ttft + stream_sec)`). |
| **Защита от буферных всплесков** | Автоматически помечает миллисекундные пакетные сбросы (`BUF < 500ms`), чтобы фиктивные пики `100,000+ tok/s` не искажали `PEAK TPS` и графики. |
| **Приоритет сырого ID модели** | Считывает protobuf-поле `f19` напрямую (например, `GEMINI-3.8-FLASH-K`) вместе с фактическим лимитом контекстного окна `f9.f10.f4` (например, `256,000`). |
| **Ноль внешних зависимостей** | Плавающий виджет и CLI работают исключительно на стандартной библиотеке Python (`sqlite3`, `tkinter`), а плагин боковой панели использует встроенный `node:sqlite`. |
| **Переключение UI EN / 中文** | По умолчанию отображает компактные английские аббревиатуры (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) с мгновенным переключением `EN / 中文`. |

---

## <a id="quick-start"></a>Быстрый старт

### 1. Нативный плагин боковой панели Antigravity 2.0

Устанавливается в `~/.gemini/config/plugins/agy-hud` как вспомогательная боковая панель с автоматической синхронизацией светлой/темной темы, гистограммой TPS и журналом вызовов:

```bash
python plugin/install_plugin.py
```

Для удаления:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Автономная плавающая панель и CLI

Работает полностью независимо без изменения плагинов Antigravity:

- **Windows GUI (без консольного окна)**: дважды щелкните `desktop/launch.bat` или `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Плавающий HUD-виджет (по умолчанию: EN, обновление каждые 500 мс)
python -m desktop.cli

# Единоразовый снимок в терминале
python -m desktop.cli --cli

# Непрерывный мониторинг в терминале
python -m desktop.cli --watch
```

> [!TIP]
> Нажмите **правой кнопкой мыши** в любом месте плавающего виджета, чтобы переключить **Язык (`EN` / `中文`)**, **Поверх всех окон**, **Закрепить позицию**, **Прозрачность (`100%`–`50%`)** или **Частоту обновления (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Карта телеметрии Protobuf

AGY-HUD извлекает достоверные поля генерации напрямую из `~/.gemini/antigravity/conversations/<uuid>.db`:

| Путь поля | Извлекаемая метрика | Резервный источник |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Сырой обнаруженный идентификатор модели (`gemini-3.8-flash-k`) | Отображаемое имя `f1.f21` |
| `gen_metadata.f1.f4` | `f5` кэш, `f2` новый ввод, `f3` вывод, `f9` размышления, `f10` видимый текст | Устаревший формат `f1.f17.f2` |
| `gen_metadata.f1.f9.f10` | `f1` активный размер контекста, `f4` лимит окна (`256,000`) | Таблица лимитов моделей |
| `gen_metadata.f1.f11` / `f12` | `TTFT` и длительность потоковой генерации `Duration` | `0.0s` |
| `steps` (последний активный) | Текущее время выполнения активного шага планировщика (`step_type = 15`) | Состояние простоя |

---

## Структура репозитория

```text
agy-hud/
├── desktop/                     # Плавающий виджет и CLI на Python без зависимостей
│   ├── telemetry.py             # Декодер SQLite+WAL (только чтение) и protobuf
│   ├── hud_pill.py              # Безрамочный виджет Tkinter и карточка EN/中文
│   ├── cli.py                   # Точка входа GUI / --cli / --watch
│   ├── launch.pyw               # Тихий запуск Windows GUI без консоли
│   └── launch.bat               # Пакетный запуск для Windows по двойному клику
├── plugin/                      # Нативный UI-плагин боковой панели Antigravity 2.0
│   ├── plugin.json              # Манифест плагина Antigravity
│   ├── install_plugin.py        # Установщик / деинсталлятор одной командой
│   ├── assets/logo.svg          # Векторная эмблема циферблата
│   └── sidecars/hud_panel/      # Бэкенд node:sqlite и Webview-панель
├── docs/
│   └── assets/                  # SVG-баннер и превью интерфейса
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Лицензия

Распространяется под лицензией [MIT License](LICENSE).
