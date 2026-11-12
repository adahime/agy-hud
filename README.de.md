<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD Banner" width="100%" />

<p>
  <strong>Echtzeit-HUD für Token/s, TTFT, rohe Modell-ID und Kontextfenster in Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Lizenz: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js integriertes SQLite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Keine Abhängigkeiten" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="Dokumentation in 8 Sprachen" />
</p>

<p>
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <strong>Deutsch</strong> ·
  <a href="README.ru.md">Русский</a>
</p>

<p>
  <a href="#overview">Überblick</a> ·
  <a href="#quick-start">Schnellstart</a> ·
  <a href="#protobuf-map">Protobuf-Zuordnung</a> ·
  <a href="CHANGELOG.md">Änderungsprotokoll</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="Vorschau von AGY-HUD Desktop-Pill und nativem Seitenpanel" width="100%" />
</div>

---

## <a id="overview"></a>Warum AGY-HUD?

Die meisten Token-Zähler leiten API-Datenverkehr über einen Proxy um oder schätzen Token-Größen mit clientseitigen Tokenizern. **AGY-HUD** liest die lokalen SQLite + WAL Konversationsdatenbanken von Google Antigravity direkt im strikten Nur-Lese-Modus (`?mode=ro`) aus und dekodiert die auf der Festplatte gespeicherten binären Protobuf-Datensätze `gen_metadata` und `steps`.

| Funktion | Details |
| :--- | :--- |
| **Duale TPS-Metriken** | Misst sowohl die reine Streaming-Geschwindigkeit (`GEN TPS = output / stream_sec`) als auch die gefühlte Ende-zu-Ende-Rate (`E2E TPS = output / (ttft + stream_sec)`). |
| **Schutz vor gepufferten Bursts** | Markiert automatisch einzelne Millisekunden-Paket-Flushes (`BUF < 500ms`), damit künstliche `100,000+ tok/s`-Spitzen weder `PEAK TPS` noch Diagramme verfälschen. |
| **Priorität für rohe Modell-ID** | Liest das Protobuf-Feld `f19` direkt aus (z. B. `GEMINI-3.8-FLASH-K`) zusammen mit dem realen Kontextbudget `f9.f10.f4` (z. B. `256,000`). |
| **Keine externen Abhängigkeiten** | Desktop-Pill und CLI nutzen ausschließlich die Python-Standardbibliothek (`sqlite3`, `tkinter`); das Seitenpanel-Plugin nutzt das in Node.js integrierte `node:sqlite`. |
| **Live-Umschaltung EN / 中文** | Verwendet standardmäßig kompakte englische Fachkürzel (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) mit direktem `EN / 中文`-Wechsel. |

---

## <a id="quick-start"></a>Schnellstart

### 1. Natives Antigravity 2.0 Seitenpanel-Plugin

Wird unter `~/.gemini/config/plugins/agy-hud` als Seitenpanel-Ansicht mit automatischer Hell/Dunkel-Themenanpassung, TPS-Balkendiagramm und Aufrufprotokoll installiert:

```bash
python plugin/install_plugin.py
```

Zum Deinstallieren:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Eigenständige Desktop-Pill & CLI

Läuft völlig unabhängig, ohne Antigravity-Plugins zu verändern:

- **Windows-GUI (ohne Konsolenfenster)**: Doppelklick auf `desktop/launch.bat` oder `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Schwebende HUD-Pill starten (Standard: EN, 500 ms Aktualisierung)
python -m desktop.cli

# Einmaliger Terminal-Snapshot
python -m desktop.cli --cli

# Fortlaufende Live-Überwachung im Terminal
python -m desktop.cli --watch
```

> [!TIP]
> Ein **Rechtsklick** auf eine beliebige Stelle der Desktop-Pill öffnet Optionen für **Sprache (`EN` / `中文`)**, **Immer im Vordergrund**, **Position fixieren**, **Deckkraft (`100%`–`50%`)** und **Aktualisierungsrate (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Protobuf-Telemetrie-Zuordnung

AGY-HUD extrahiert unverfälschte Generierungsfelder direkt aus `~/.gemini/antigravity/conversations/<uuid>.db`:

| Feldpfad | Extrahierte Metrik | Fallback |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Rohe erkannte Modell-ID (`gemini-3.8-flash-k`) | `f1.f21` Anzeigename |
| `gen_metadata.f1.f4` | `f5` Cache, `f2` neuer Input, `f3` Output, `f9` Thinking, `f10` sichtbar | `f1.f17.f2` Legacy-Zähler |
| `gen_metadata.f1.f9.f10` | `f1` aktive Kontextgröße, `f4` Fensterlimit (`256,000`) | Modell-Limit-Tabelle |
| `gen_metadata.f1.f11` / `f12` | `TTFT` und Streaming-Generierungsdauer `Duration` | `0.0s` |
| `steps` (letzter aktiver Schritt) | Laufzeit des aktiven Planer-Schritts (`step_type = 15`) | Leerlauf |

---

## Repository-Struktur

```text
agy-hud/
├── desktop/                     # Abhängigkeitsfreie Python Desktop-Pill & CLI
│   ├── telemetry.py             # Nur-Lese SQLite+WAL & Protobuf-Decoder
│   ├── hud_pill.py              # Rahmenlose Tkinter-Pill & EN/中文-Karten-UI
│   ├── cli.py                   # Einstiegspunkt für GUI / --cli / --watch
│   ├── launch.pyw               # Stiller Windows-GUI-Starter
│   └── launch.bat               # Windows-Doppelklick-Starter
├── plugin/                      # Natives Antigravity 2.0 Seitenpanel-UI-Plugin
│   ├── plugin.json              # Antigravity-Plugin-Manifest
│   ├── install_plugin.py        # Ein-Befehl-Installer / Deinstaller
│   ├── assets/logo.svg          # Vektor-Tacho-Emblem
│   └── sidecars/hud_panel/      # node:sqlite Backend & Webview-Dashboard
├── docs/
│   └── assets/                  # SVG-Banner & UI-Vorschaugrafiken
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Lizenz

Veröffentlicht unter der [MIT License](LICENSE).
