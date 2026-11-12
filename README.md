<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD Banner" width="100%" />

<p>
  <strong>Real-time token speed, TTFT, actual routed model ID, and context window monitor for Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="License: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-22.5%2B%20node%3Asqlite-06b6d4?style=flat-square" alt="Node.js 22.5+ node:sqlite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20External-10b981?style=flat-square" alt="Zero External Dependencies" />
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

**AGY-HUD** is a lightweight desktop floating monitor, CLI tool, and side-pane plugin for Google Antigravity. It reads Antigravity's local SQLite conversation databases (`~/.gemini/antigravity/conversations/<uuid>.db` and `-wal`) strictly in read-only mode to display generation speed, time to first token (`TTFT`), the **actual routed backend model ID**, and context window usage without proxying API requests.

### Key Features

- **Actual Routed Model ID First**: Prioritizes protobuf field `f19`—the actual routed backend model identifier (such as `gemini-3.8-flash-k`)—instead of the UI display label in `f21` (which is used only as a fallback when `f19` is absent). Also reads the reported context limit from `f9.f10.f4` (for example `256,000`), falling back to a built-in table only when omitted.
- **Generation & End-to-End Speed**: Reports both streaming throughput after the first token (`GEN TPS = output / stream_sec`) and overall speed including initial wait (`E2E TPS = output / (ttft + stream_sec)`). Responses finishing in under `0.5s` (or under `1.0s` above `1,200 tok/s`) are flagged as buffered (`BUF`), excluded from peak `GEN TPS`, and plotted/shown using `E2E` speed plus the previous sustained streaming speed (`STR`).
- **Read-Only Local Database Access**: The Python desktop app and CLI open databases via SQLite URI `?mode=ro` and track `.db` / `.db-wal` modification times; the Antigravity side-pane plugin opens them via Node.js `node:sqlite` (`{ readOnly: true }`). No API keys or network proxies required.
- **Zero External Packages**: The desktop floating window and CLI use only Python 3.9+ standard library (`sqlite3`, `tkinter`), while the side-pane plugin uses Antigravity's built-in `sidecar_sdk` and Node.js 22.5+ built-in `node:sqlite`. No `pip install` or `npm install` needed.
- **Desktop Pill, CLI & Side-Pane Plugin**: The side-pane view follows light/dark themes automatically, lets you switch between `Auto Pane`, `Latest DB`, or the 15 most recent conversations, and renders a 28-turn bar chart plus a 30-turn call log. Both the desktop window and plugin default to concise English labels (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) and switch cleanly between `EN` and `中文`.

---

## <a id="quick-start"></a>Quick Start

### 1. Antigravity 2.0 Side-Pane Plugin

Install into `~/.gemini/config/plugins/agy-hud` (reload/restart Antigravity if the icon does not appear immediately):

```bash
python plugin/install_plugin.py
```

To uninstall:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Standalone Desktop Window & CLI

Runs independently without touching any Antigravity plugin configuration:

- **Windows (no console window)**: double-click `desktop/launch.bat` or `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Launch desktop floating pill (default: EN, 500ms refresh, 92% opacity)
python -m desktop.cli

# Optional flags: --lang en|zh, --refresh-ms 500, --alpha 0.92
python -m desktop.cli --lang zh --refresh-ms 1000

# Print one snapshot to the terminal and exit
python -m desktop.cli --cli

# Stream a summary line whenever a new turn finishes (--interval defaults to 1.0s)
python -m desktop.cli --watch --interval 1.0
```

> [!TIP]
> Left-drag the pill header to move it (unless pinned), click `▾` or double-click the text to expand/collapse details, and **right-click** anywhere on the window to adjust **Language (`EN` / `中文`)**, **Always on Top**, **Pin Position**, **Opacity (`100%`–`50%`)**, or **Refresh Rate (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Data Fields

AGY-HUD reads `gen_metadata` and `steps` from `~/.gemini/antigravity/conversations/<uuid>.db`:

| Field Path | Decoded Data | Fallback |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | **Routed backend model identifier** (e.g. `gemini-3.8-flash-k`) | UI display label (`f1.f21`) |
| `gen_metadata.f1.f4` | Cached (`f5`), new input (`f2`), output (`f3` or `f1`), thinking (`f9`), visible (`f10`) | Legacy usage (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Active context size (`f1`) and window limit (`f4`, e.g. `256,000`) | `cached + new_input`; per-model limit table |
| `gen_metadata.f1.f11` / `f1.f12` | Time to first token (`TTFT`, `f11`) and streaming duration (`f12`) | `0.0s` |
| `steps` (`status != 3`) | Active generation timer (`step_type = 15`); side-pane plugin also shows `TOOL` on other non-terminal steps and maps timestamps via `f1.f20` | Idle state |

---

## Project Structure

```text
agy-hud/
├── desktop/                     # Python 3.9+ stdlib floating window & CLI
│   ├── telemetry.py             # Read-only SQLite (?mode=ro) + WAL & protobuf parser
│   ├── hud_pill.py              # Tkinter frameless pill, detail card & EN/中文 UI
│   ├── cli.py                   # Entrypoint for GUI / --cli / --watch
│   ├── launch.pyw               # Silent Windows GUI launcher
│   └── launch.bat               # Windows double-click batch launcher
├── plugin/                      # Antigravity 2.0 side-pane plugin
│   ├── plugin.json              # Plugin manifest
│   ├── install_plugin.py        # Installer / uninstaller script
│   ├── assets/logo.svg          # Plugin icon
│   └── sidecars/hud_panel/      # node:sqlite backend (450ms poll, ETag) & Webview UI
├── docs/
│   └── assets/                  # SVG banner and preview graphics
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## License

Released under the [MIT License](LICENSE).
