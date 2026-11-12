<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD Banner" width="100%" />

<p>
  <strong>Echtzeit-Monitor für Token-Geschwindigkeit, TTFT, aktives Modell und Kontextauslastung in Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Lizenz: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Standardbibliothek" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js integriertes SQLite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Keine externen Abhängigkeiten" />
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

**AGY-HUD** ist ein schlanker schwebender Desktop-Monitor, ein CLI-Tool und ein Seitenpanel-Plugin für Google Antigravity. Es liest lokale SQLite-Datenbanken direkt im Nur-Lese-Modus (`?mode=ro`) aus, um Token-Geschwindigkeit, Zeit bis zum ersten Token (`TTFT`), aktives Modell und Kontextauslastung anzuzeigen, ohne den Netzwerkverkehr umzuleiten.

### Hauptfunktionen

- **Lokale Daten im Nur-Lese-Modus**: Liest `~/.gemini/antigravity/conversations/<uuid>.db` im Nur-Lese-Modus (`?mode=ro`). Keine API-Schlüssel und keine Proxy-Einrichtung erforderlich.
- **Generierungs- und Gesamtgeschwindigkeit**: Zeigt sowohl die reine Streaming-Rate nach dem ersten Token (`GEN TPS = Ausgabe / Stream-Dauer`) als auch die Gesamtgeschwindigkeit inklusive Startlatenz (`E2E TPS = Ausgabe / (TTFT + Stream-Dauer)`). Antworten unter 500 ms werden als `BUF` gekennzeichnet, damit kurze Ausbrüche die Maximalwerte nicht verzerren.
- **Genaue Modell- und Kontexterkennung**: Liest die erkannte Modellkennung direkt aus Feld `f19` (z. B. `gemini-3.8-flash-k`) sowie das gemeldete Kontextlimit aus `f9.f10.f4` (z. B. `256,000`).
- **Keine externen Abhängigkeiten**: Desktop-Fenster und CLI verwenden ausschließlich die Python-Standardbibliothek (`sqlite3`, `tkinter`), das Seitenpanel-Plugin nutzt das in Node.js integrierte `node:sqlite`. Weder `pip install` noch `npm install` sind nötig.
- **Englische & chinesische Oberfläche**: Verwendet standardmäßig kompakte englische Abkürzungen (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) und ermöglicht den Wechsel zwischen Englisch und Chinesisch über das Kontextmenü oder die Panel-Kopfzeile.

---

## <a id="quick-start"></a>Schnellstart

### 1. Antigravity 2.0 Seitenpanel-Plugin

Installiert das Plugin in `~/.gemini/config/plugins/agy-hud`, um TPS-Diagramme und aktuelle Einträge direkt im Seitenpanel anzuzeigen (passt sich automatisch an helle und dunkle Designs an):

```bash
python plugin/install_plugin.py
```

Zum Deinstallieren:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Eigenständiges Desktop-Fenster & CLI

Läuft unabhängig, ohne bestehende Antigravity-Plugin-Einstellungen zu verändern:

- **Windows-Desktop (ohne Konsolenfenster)**: Doppelklick auf `desktop/launch.bat` oder `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Schwebendes Desktop-Fenster starten (Standard: Englisch, 500 ms Aktualisierung)
python -m desktop.cli

# Einzelnen Status im Terminal ausgeben
python -m desktop.cli --cli

# Fortlaufend im Terminal aktualisieren
python -m desktop.cli --watch
```

> [!TIP]
> Ein **Rechtsklick** an beliebiger Stelle im schwebenden Fenster öffnet die Einstellungen für **Sprache (`EN` / `中文`)**, **Immer im Vordergrund**, **Position fixieren**, **Transparenz (`100%`–`50%`)** und **Aktualisierungsrate (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Datenfelder

AGY-HUD liest folgende Felder aus `~/.gemini/antigravity/conversations/<uuid>.db`:

| Feldpfad | Wert | Fallback |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Erkannte Modellkennung (`gemini-3.8-flash-k`) | Anzeigename (`f1.f21`) |
| `gen_metadata.f1.f4` | Cache (`f5`), neue Eingabe (`f2`), Ausgabe (`f3`), Denken (`f9`), sichtbar (`f10`) | Älteres Zählformat (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Aktuelle Kontextnutzung (`f1`) und Limit (`f4`, z. B. `256,000`) | Modell-Limit-Tabelle |
| `gen_metadata.f1.f11` / `f12` | Zeit bis zum ersten Token (`TTFT`) und Streaming-Dauer | `0.0s` |
| `steps` (neueste aktive Zeile) | Verstrichene Zeit des laufenden Schritts (`step_type = 15`) | Leerlauf |

---

## Projektstruktur

```text
agy-hud/
├── desktop/                     # Desktop-Fenster & CLI mit Python-Standardbibliothek
│   ├── telemetry.py             # Nur-Lese SQLite + WAL und Protobuf-Parser
│   ├── hud_pill.py              # Schwebendes Tkinter-Fenster & Detailansicht
│   ├── cli.py                   # Einstiegspunkt für GUI / --cli / --watch
│   ├── launch.pyw               # Hintergrund-Starter für Windows ohne Konsole
│   └── launch.bat               # Windows-Batch-Starter per Doppelklick
├── plugin/                      # Antigravity 2.0 Seitenpanel-Plugin
│   ├── plugin.json              # Plugin-Manifest
│   ├── install_plugin.py        # Installations- und Deinstallationsskript
│   ├── assets/logo.svg          # Plugin-Symbol
│   └── sidecars/hud_panel/      # node:sqlite Backend und Webview-Oberfläche
├── docs/
│   └── assets/                  # SVG-Banner und Vorschaubilder
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Lizenz

Veröffentlicht unter der [MIT License](LICENSE).
