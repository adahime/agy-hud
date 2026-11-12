<div align="center">

<img src="docs/assets/banner.svg" alt="Bannière AGY-HUD" width="100%" />

<p>
  <strong>HUD en temps réel des Token/s, TTFT, ID brut du modèle et fenêtre de contexte pour Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Licence : MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="SQLite intégré Node.js" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Zéro dépendance" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="Documentation en 8 langues" />
</p>

<p>
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <strong>Français</strong> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ru.md">Русский</a>
</p>

<p>
  <a href="#overview">Présentation</a> ·
  <a href="#quick-start">Démarrage rapide</a> ·
  <a href="#protobuf-map">Carte Protobuf</a> ·
  <a href="CHANGELOG.md">Journal des modifications</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="Aperçu de la pilule bureau et du panneau latéral natif AGY-HUD" width="100%" />
</div>

---

## <a id="overview"></a>Pourquoi AGY-HUD ?

La plupart des compteurs de jetons interceptent votre trafic API via un proxy ou estiment la taille avec des tokenizers côté client. **AGY-HUD** lit directement les bases de données locales SQLite + WAL de Google Antigravity en mode lecture seule stricte (`?mode=ro`) et décode les enregistrements protobuf `gen_metadata` et `steps` stockés sur le disque.

| Fonctionnalité | Détails |
| :--- | :--- |
| **Double métrique TPS** | Mesure à la fois le débit pur de streaming (`GEN TPS = output / stream_sec`) et la vitesse perçue de bout en bout (`E2E TPS = output / (ttft + stream_sec)`). |
| **Garde anti-pics en mémoire tampon** | Signale automatiquement les rafales en paquet unique de quelques millisecondes (`BUF < 500ms`) afin que les pics artificiels à `100,000+ tok/s` ne faussent ni `PEAK TPS` ni les graphiques. |
| **Priorité à l'ID brut du modèle** | Lit directement le champ protobuf `f19` (par ex. `GEMINI-3.8-FLASH-K`) ainsi que le budget réel de la fenêtre de contexte `f9.f10.f4` (par ex. `256,000`). |
| **Zéro dépendance externe** | La pilule flottante et la CLI s'appuient uniquement sur la bibliothèque standard Python (`sqlite3`, `tkinter`) ; le plugin latéral utilise `node:sqlite` intégré à Node.js. |
| **Bascule UI EN / 中文 instantanée** | Affiche par défaut des abréviations techniques compactes en anglais (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`), avec commutation instantanée `EN / 中文`. |

---

## <a id="quick-start"></a>Démarrage rapide

### 1. Plugin natif de panneau latéral pour Antigravity 2.0

S'installe dans `~/.gemini/config/plugins/agy-hud` comme vue auxiliaire du panneau latéral avec synchronisation automatique du thème clair/sombre, histogramme TPS et journal des appels :

```bash
python plugin/install_plugin.py
```

Pour désinstaller :

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Pilule flottante autonome et CLI

Fonctionne de manière totalement autonome sans modifier les plugins d'Antigravity :

- **GUI Windows (sans fenêtre de console)** : double-cliquez sur `desktop/launch.bat` ou `desktop/launch.pyw`
- **Python GUI / CLI** :

```bash
# Pilule HUD flottante (par défaut : EN, rafraîchissement 500 ms)
python -m desktop.cli

# Instantané unique dans le terminal
python -m desktop.cli --cli

# Suivi continu en direct dans le terminal
python -m desktop.cli --watch
```

> [!TIP]
> Effectuez un **clic droit** n'importe où sur la pilule flottante pour régler la **Langue (`EN` / `中文`)**, **Toujours au premier plan**, **Verrouiller la position**, l'**Opacité (`100%`–`50%`)** ou la **Fréquence de rafraîchissement (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Carte de télémétrie Protobuf

AGY-HUD extrait les champs de génération de référence depuis `~/.gemini/antigravity/conversations/<uuid>.db` :

| Chemin du champ | Métrique extraite | Repli (Fallback) |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Identifiant brut du modèle détecté (`gemini-3.8-flash-k`) | Nom d'affichage `f1.f21` |
| `gen_metadata.f1.f4` | `f5` en cache, `f2` nouvelle entrée, `f3` sortie, `f9` réflexion, `f10` visible | Ancien format `f1.f17.f2` |
| `gen_metadata.f1.f9.f10` | `f1` contexte actif, `f4` limite de fenêtre (`256,000`) | Table de limites par modèle |
| `gen_metadata.f1.f11` / `f12` | `TTFT` et durée de génération en flux `Duration` | `0.0s` |
| `steps` (dernier non terminal) | Compteur écoulé en direct de l'étape active (`step_type = 15`) | État inactif |

---

## Structure du dépôt

```text
agy-hud/
├── desktop/                     # Pilule bureau et CLI Python sans dépendances
│   ├── telemetry.py             # Décodeur SQLite+WAL lecture seule & protobuf
│   ├── hud_pill.py              # Pilule Tkinter sans bordure & carte EN/中文
│   ├── cli.py                   # Point d'entrée GUI / --cli / --watch
│   ├── launch.pyw               # Lanceur GUI Windows silencieux
│   └── launch.bat               # Lanceur Windows par double-clic
├── plugin/                      # Plugin natif de panneau latéral Antigravity 2.0
│   ├── plugin.json              # Manifeste du plugin Antigravity
│   ├── install_plugin.py        # Installateur / désinstallateur en une commande
│   ├── assets/logo.svg          # Emblème vectoriel du cadran
│   └── sidecars/hud_panel/      # Backend node:sqlite & tableau de bord Webview
├── docs/
│   └── assets/                  # Bannière SVG & aperçus visuels de l'interface
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Licence

Distribué sous licence [MIT License](LICENSE).
