<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD Banner" width="100%" />

<p>
  <strong>Echtzeit-Monitor für Token-Geschwindigkeit, TTFT, tatsächliche geroutete Modell-ID und Kontextauslastung in Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Lizenz: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Standardbibliothek" />
  <img src="https://img.shields.io/badge/Node.js-22.5%2B%20node%3Asqlite-06b6d4?style=flat-square" alt="Node.js 22.5+ node:sqlite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20External-10b981?style=flat-square" alt="Keine externen Pakete" />
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
  <a href="#protobuf-map">Datenfelder</a> ·
  <a href="CHANGELOG.md">Änderungsprotokoll</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="Vorschau des schwebenden Desktop-Fensters und Seitenpanels von AGY-HUD" width="100%" />
</div>

---

## <a id="overview"></a>Überblick

**AGY-HUD** ist ein schlanker schwebender Desktop-Monitor, ein CLI-Tool und ein Seitenpanel-Plugin für Google Antigravity. Es liest lokale SQLite-Datenbanken (`~/.gemini/antigravity/conversations/<uuid>.db` samt `-wal`) strikt im Nur-Lese-Modus aus und zeigt Token-Geschwindigkeit, Zeit bis zum ersten Token (`TTFT`), die **tatsächlich geroutete Backend-Modell-ID** und die Kontextauslastung ohne Umleitung des Netzwerkverkehrs an.

### Hauptfunktionen

- **Tatsächlich geroutete Modell-ID zuerst**: Priorisiert das Protobuf-Feld `f19`—die tatsächlich im Backend angesteuerte Modellkennung (z. B. `gemini-3.8-flash-k`)—statt des Anzeigenamens in der Oberfläche (`f21`, der nur als Fallback dient, wenn `f19` fehlt). Liest zudem das gemeldete Kontextlimit direkt aus `f9.f10.f4` (z. B. `256,000`).
- **Generierungs- und Gesamtgeschwindigkeit**: Berechnet sowohl die reine Streaming-Rate nach dem ersten Token (`GEN TPS = Ausgabe / Stream-Dauer`) als auch die Gesamtrate inklusive Startlatenz (`E2E TPS = Ausgabe / (TTFT + Stream-Dauer)`). Antworten unter `0.5s` (oder unter `1.0s` bei über `1,200 tok/s`) werden als `BUF` markiert, aus `PEAK TPS` ausgeschlossen und stattdessen über `E2E` sowie die letzte anhaltende Streaming-Rate (`STR`) dargestellt.
- **Lokaler Nur-Lese-Zugriff**: Desktop-Fenster und CLI in Python öffnen Datenbanken per SQLite-URI `?mode=ro` und überwachen Änderungszeiten von `.db` und `.db-wal`; das Seitenpanel-Plugin nutzt Node.js `node:sqlite` mit `{ readOnly: true }`. Weder API-Schlüssel noch Proxy-Konfiguration nötig.
- **Keine externen Pakete**: Desktop-Fenster und CLI nutzen ausschließlich die Python-3.9+-Standardbibliothek (`sqlite3`, `tkinter`), während das Seitenpanel-Plugin das in Antigravity enthaltene `sidecar_sdk` und Node.js 22.5+ `node:sqlite` verwendet. Kein `pip install` oder `npm install` erforderlich.
- **Desktop-Fenster, CLI & Seitenpanel-Plugin**: Das Seitenpanel passt sich automatisch an helle und dunkle Designs an, erlaubt den Wechsel zwischen `Auto Pane`, `Latest DB` oder den 15 zuletzt aktiven Konversationen und zeigt ein Balkendiagramm der letzten 28 Aufrufe sowie eine Historie über 30 Einträge. Beide Oberflächen nutzen standardmäßig knappe englische Kürzel (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) und unterstützen die Umschaltung zwischen `EN` und `中文`.

---

## <a id="quick-start"></a>Schnellstart

### 1. Antigravity 2.0 Seitenpanel-Plugin

Installiert das Plugin in `~/.gemini/config/plugins/agy-hud` (falls das Symbol nicht sofort erscheint, Antigravity neu laden oder neu starten):

```bash
python plugin/install_plugin.py
```

Zum Deinstallieren:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Eigenständiges Desktop-Fenster & CLI

Läuft unabhängig, ohne bestehende Antigravity-Plugin-Einstellungen zu verändern:

- **Windows (ohne Konsolenfenster)**: Doppelklick auf `desktop/launch.bat` oder `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Schwebendes Desktop-Fenster starten (Standard: EN, 500 ms Aktualisierung, 92 % Deckkraft)
python -m desktop.cli

# Optionale Parameter: --lang en|zh, --refresh-ms 500, --alpha 0.92
python -m desktop.cli --lang zh --refresh-ms 1000

# Einzelnen Status im Terminal ausgeben und beenden
python -m desktop.cli --cli

# Bei jeder abgeschlossenen Antwort eine Zeile ausgeben (--interval Standard: 1.0 s)
python -m desktop.cli --watch --interval 1.0
```

> [!TIP]
> Die obere Leiste per Linksklick verschieben (sofern nicht fixiert), über `▾` oder Doppelklick auf den Text die Details auf-/zuklappen und per **Rechtsklick** an beliebiger Stelle **Sprache (`EN` / `中文`)**, **Immer im Vordergrund**, **Position fixieren**, **Transparenz (`100%`–`50%`)** oder **Aktualisierungsrate (`0.5s`–`5s`)** einstellen.

---

## <a id="protobuf-map"></a>Datenfelder

AGY-HUD liest `gen_metadata` und `steps` aus `~/.gemini/antigravity/conversations/<uuid>.db`:

| Feldpfad | Wert | Fallback |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | **Tatsächlich geroutete Backend-Modell-ID** (z. B. `gemini-3.8-flash-k`) | UI-Anzeigename (`f1.f21`) |
| `gen_metadata.f1.f4` | Cache (`f5`), neue Eingabe (`f2`), Ausgabe (`f3` oder `f1`), Denken (`f9`), sichtbar (`f10`) | Älteres Zählformat (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Aktive Kontextgröße (`f1`) und Fensterlimit (`f4`, z. B. `256,000`) | `Cache + neue Eingabe`; Modell-Limit-Tabelle |
| `gen_metadata.f1.f11` / `f1.f12` | Zeit bis zum ersten Token (`TTFT`, `f11`) und Streaming-Dauer (`f12`) | `0.0s` |
| `steps` (`status != 3`) | Laufzeit des aktiven Generierungsschritts (`step_type = 15`); im Seitenpanel auch `TOOL`-Anzeige bei anderen aktiven Schritten und Zeitstempel über `f1.f20` | Leerlauf |

---

## Projektstruktur

```text
agy-hud/
├── desktop/                     # Desktop-Fenster & CLI auf Basis von Python 3.9+ Stdlib
│   ├── telemetry.py             # Nur-Lese SQLite (?mode=ro) + WAL und Protobuf-Parser
│   ├── hud_pill.py              # Rahmenloses Tkinter-Fenster, Detailkarte & EN/中文 UI
│   ├── cli.py                   # Einstiegspunkt für GUI / --cli / --watch
│   ├── launch.pyw               # Stiller Hintergrund-Starter für Windows
│   └── launch.bat               # Windows-Batch-Starter per Doppelklick
├── plugin/                      # Antigravity 2.0 Seitenpanel-Plugin
│   ├── plugin.json              # Plugin-Manifest
│   ├── install_plugin.py        # Installations- und Deinstallationsskript
│   ├── assets/logo.svg          # Plugin-Symbol
│   └── sidecars/hud_panel/      # node:sqlite Backend (450 ms Abruf, ETag) & Webview-UI
├── docs/
│   └── assets/                  # SVG-Banner und Vorschaubilder
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Lizenz

Veröffentlicht unter der [MIT License](LICENSE).
