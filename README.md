<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD Banner" width="100%" />

<p>
  <strong>Real-Time Token/s, TTFT, Raw Model ID &amp; Context Window HUD for Google Antigravity</strong>
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
  <a href="#protobuf-map">Protobuf Map</a> ·
  <a href="CHANGELOG.md">Changelog</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="AGY-HUD Desktop Pill and Native Side-Pane Preview" width="100%" />
</div>

---

## <a id="overview"></a>Why AGY-HUD?

Most token counters proxy your API traffic or estimate token sizes with client-side tokenizers. **AGY-HUD** reads Google Antigravity's local SQLite + WAL conversation databases directly in strict read-only mode (`?mode=ro`) and decodes the wire-format protobuf `gen_metadata` and `steps` records stored on disk.

| Capability | Details |
| :--- | :--- |
| **Dual TPS Metrics** | Measures both pure streaming throughput (`GEN TPS = output / stream_sec`) and perceived end-to-end speed (`E2E TPS = output / (ttft + stream_sec)`). |
| **Buffered Burst Guard** | Automatically flags single-packet millisecond tool flushes (`BUF < 500ms`) so artificial `100,000+ tok/s` spikes never distort `PEAK TPS` or charts. |
| **Raw Model ID Priority** | Reads protobuf field `f19` directly (e.g. `GEMINI-3.8-FLASH-K`) alongside the real context window budget `f9.f10.f4` (e.g. `256,000`). |
| **Zero Dependencies** | Desktop floating pill & CLI rely exclusively on Python stdlib (`sqlite3`, `tkinter`); the Antigravity side-pane plugin uses Node's built-in `node:sqlite`. |
| **Live EN / 中文 UI Toggle** | Defaults to compact technical English abbreviations (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`), with instant `EN / 中文` switching. |

---

## <a id="quick-start"></a>Quick Start

### 1. Native Antigravity 2.0 Side-Pane Plugin

Installs into `~/.gemini/config/plugins/agy-hud` as an auxiliary side-pane view with adaptive light/dark theme sync, TPS bar chart, and call log:

```bash
python plugin/install_plugin.py
```

To uninstall:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Standalone Desktop Floating Pill & CLI

Runs completely independently without modifying Antigravity plugins:

- **Windows GUI (no console window)**: double-click `desktop/launch.bat` or `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Floating HUD pill (default: EN, 500ms refresh)
python -m desktop.cli

# Single-shot terminal snapshot
python -m desktop.cli --cli

# Streaming terminal watch
python -m desktop.cli --watch
```

> [!TIP]
> Right-click anywhere on the floating pill to toggle **Language (`EN` / `中文`)**, **Always on Top**, **Pin Position**, **Opacity (`100%`–`50%`)**, or **Refresh Rate (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Protobuf Telemetry Map

AGY-HUD extracts ground-truth generation fields from `~/.gemini/antigravity/conversations/<uuid>.db`:

| Field Path | Extracted Metric | Fallback |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Raw detected model identifier (`gemini-3.8-flash-k`) | `f1.f21` display name |
| `gen_metadata.f1.f4` | `f5` cached, `f2` new input, `f3` output, `f9` thinking, `f10` visible | `f1.f17.f2` legacy usage |
| `gen_metadata.f1.f9.f10` | `f1` active context size, `f4` window limit (`256,000`) | Model limit lookup table |
| `gen_metadata.f1.f11` / `f12` | `TTFT` and streaming generation `Duration` | `0.0s` |
| `steps` (latest non-terminal) | Active planner step (`step_type = 15`) live elapsed counter | Idle state |

---

## Repository Structure

```text
agy-hud/
├── desktop/                     # Zero-dependency Python Desktop Pill & CLI
│   ├── telemetry.py             # Read-only SQLite+WAL & protobuf decoder
│   ├── hud_pill.py              # Frameless Tkinter pill & EN/中文 card UI
│   ├── cli.py                   # GUI / --cli / --watch entrypoint
│   ├── launch.pyw               # Silent Windows GUI launcher
│   └── launch.bat               # Double-click Windows launcher
├── plugin/                      # Native Antigravity 2.0 Side-Pane UI Plugin
│   ├── plugin.json              # Antigravity plugin manifest
│   ├── install_plugin.py        # One-command installer / uninstaller
│   ├── assets/logo.svg          # Vector dial emblem
│   └── sidecars/hud_panel/      # node:sqlite backend & Webview dashboard
├── docs/
│   └── assets/                  # SVG banner & UI preview graphics
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## License

Released under the [MIT License](LICENSE).
