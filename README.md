<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD Banner" width="100%" />

<p>
  <strong>Real-time token speed, TTFT, active model, and context window monitor for Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="License: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js Built-in SQLite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="Docs: 8 Languages" />
</p>

<p>
  <strong>English</strong> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ru.md">Русский</a>
</p>

<p>
  <a href="#overview">Overview</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#protobuf-map">Data Fields</a> ·
  <a href="CHANGELOG.md">Changelog</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="AGY-HUD Desktop Pill and Side-Pane Preview" width="100%" />
</div>

---

## <a id="overview"></a>Overview

**AGY-HUD** is a lightweight desktop floating monitor, CLI tool, and side-pane plugin for Google Antigravity. It reads local SQLite conversation databases directly in read-only mode (`?mode=ro`) to display token generation speed, time to first token (`TTFT`), active model ID, and context window usage without proxying network traffic.

### Key Features

- **Read-Only Local Data**: Reads `~/.gemini/antigravity/conversations/<uuid>.db` in read-only mode (`?mode=ro`). No API keys or proxy setup required.
- **Generation & End-to-End Speed**: Tracks both pure streaming speed (`GEN TPS = output / stream_sec`) and overall end-to-end speed including initial latency (`E2E TPS = output / (ttft + stream_sec)`). Responses delivered in under 500 ms are labeled as buffered (`BUF`) so brief bursts do not distort peak speed statistics.
- **Accurate Model & Context Limit**: Reads the detected model identifier from `f19` (such as `gemini-3.8-flash-k`) and the reported context window limit (`f9.f10.f4`, such as `256,000`).
- **Zero External Dependencies**: The desktop window and CLI run purely on Python's standard library (`sqlite3`, `tkinter`), while the side-pane plugin uses Node.js built-in `node:sqlite`. No `pip install` or `npm install` needed.
- **English & Chinese Interface**: Displays compact English abbreviations (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) by default, and supports switching between English and Chinese (`EN / 中文`).

---

## <a id="quick-start"></a>Quick Start

### 1. Antigravity 2.0 Side-Pane Plugin

Install the plugin into `~/.gemini/config/plugins/agy-hud` to view live charts and recent turn logs in the Antigravity side pane (automatically adapts to light and dark themes):

```bash
python plugin/install_plugin.py
```

To uninstall:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Standalone Desktop Window & CLI

Runs independently without modifying any Antigravity plugin settings:

- **Windows Desktop (without console window)**: double-click `desktop/launch.bat` or `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Launch floating desktop window (default: English, 500ms refresh)
python -m desktop.cli

# Print a single snapshot in the terminal
python -m desktop.cli --cli

# Continuously update in the terminal
python -m desktop.cli --watch
```

> [!TIP]
> Right-click anywhere on the floating window to change **Language (`EN` / `中文`)**, **Always on Top**, **Pin Position**, **Opacity (`100%`–`50%`)**, or **Refresh Rate (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Data Fields

AGY-HUD reads conversation telemetry from `~/.gemini/antigravity/conversations/<uuid>.db`:

| Field Path | Metric | Fallback |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Detected model identifier (`gemini-3.8-flash-k`) | Display name (`f1.f21`) |
| `gen_metadata.f1.f4` | Cached (`f5`), new input (`f2`), output (`f3`), thinking (`f9`), visible (`f10`) | Legacy counts (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Active context size (`f1`) and window limit (`f4`, e.g. `256,000`) | Model limit lookup table |
| `gen_metadata.f1.f11` / `f12` | Time to first token (`TTFT`) and streaming duration | `0.0s` |
| `steps` (latest active row) | Elapsed time of running generation step (`step_type = 15`) | Idle state |

---

## Project Structure

```text
agy-hud/
├── desktop/                     # Python desktop floating window & CLI
│   ├── telemetry.py             # Read-only SQLite + WAL and protobuf parser
│   ├── hud_pill.py              # Tkinter floating capsule & detail card UI
│   ├── cli.py                   # Entrypoint for GUI / --cli / --watch
│   ├── launch.pyw               # Background Windows GUI launcher
│   └── launch.bat               # Windows batch launcher
├── plugin/                      # Antigravity 2.0 side-pane plugin
│   ├── plugin.json              # Plugin manifest
│   ├── install_plugin.py        # Installer / uninstaller script
│   ├── assets/logo.svg          # Plugin icon
│   └── sidecars/hud_panel/      # node:sqlite backend and Webview UI
├── docs/
│   └── assets/                  # SVG banner and preview graphics
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## License

Released under the [MIT License](LICENSE).
