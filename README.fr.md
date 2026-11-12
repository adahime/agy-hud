<div align="center">

<img src="docs/assets/banner.svg" alt="Bannière AGY-HUD" width="100%" />

<p>
  <strong>Moniteur en temps réel de vitesse de tokens, TTFT, identifiant réel du modèle routé et fenêtre de contexte pour Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Licence : MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-22.5%2B%20node%3Asqlite-06b6d4?style=flat-square" alt="Node.js 22.5+ node:sqlite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20External-10b981?style=flat-square" alt="Aucune dépendance externe" />
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
  <a href="#protobuf-map">Champs de données</a> ·
  <a href="CHANGELOG.md">Journal des modifications</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="Aperçu de la fenêtre flottante et du panneau latéral AGY-HUD" width="100%" />
</div>

---

## <a id="overview"></a>Présentation

**AGY-HUD** est un moniteur flottant léger pour le bureau, un outil en ligne de commande et un plugin de panneau latéral pour Google Antigravity. Il lit directement les bases SQLite locales (`~/.gemini/antigravity/conversations/<uuid>.db` et `-wal`) en mode lecture seule afin d'afficher la vitesse de génération, le délai jusqu'au premier token (`TTFT`), l'**identifiant réel du modèle routé en backend** et l'occupation de la fenêtre de contexte sans relayer le trafic réseau.

### Fonctionnalités principales

- **Priorité à l'identifiant réel du modèle routé** : Donne la priorité au champ protobuf `f19`—l'identifiant réel du modèle exécuté côté backend (par exemple `gemini-3.8-flash-k`)—plutôt qu'au libellé affiché dans l'interface (`f21`, utilisé uniquement en repli si `f19` est absent). Lit également la limite de contexte réelle indiquée dans `f9.f10.f4` (par exemple `256,000`).
- **Vitesse de génération et vitesse globale** : Mesure à la fois la vitesse de diffusion après le premier token (`GEN TPS = sortie / durée_stream`) et la vitesse globale incluant l'attente initiale (`E2E TPS = sortie / (TTFT + durée_stream)`). Les réponses terminées en moins de `0.5s` (ou moins de `1.0s` au-delà de `1,200 tok/s`) sont marquées `BUF`, exclues du calcul `PEAK TPS`, et affichées avec la vitesse `E2E` ainsi que la dernière vitesse soutenue (`STR`).
- **Lecture locale en lecture seule** : La fenêtre de bureau et la CLI Python ouvrent les bases via l'URI SQLite `?mode=ro` en surveillant les modifications sur `.db` et `.db-wal` ; le plugin latéral utilise le module intégré `node:sqlite` de Node.js (`{ readOnly: true }`). Aucune clé API ni configuration de proxy requise.
- **Aucun paquet externe** : La fenêtre de bureau et la CLI reposent uniquement sur la bibliothèque standard Python 3.9+ (`sqlite3`, `tkinter`), et le plugin latéral utilise `sidecar_sdk` intégré à Antigravity avec `node:sqlite` de Node.js 22.5+. Aucun `pip install` ni `npm install` n'est nécessaire.
- **Fenêtre flottante, CLI et panneau latéral** : Le panneau latéral suit automatiquement les thèmes clair/sombre, permet de basculer entre `Auto Pane`, `Latest DB` ou les 15 conversations les plus récentes, et affiche un graphique sur les 28 derniers tours ainsi qu'un historique de 30 appels. Les deux interfaces utilisent par défaut des abréviations anglaises concises (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) et permettent de passer de `EN` à `中文`.

---

## <a id="quick-start"></a>Démarrage rapide

### 1. Plugin de panneau latéral pour Antigravity 2.0

Installez dans `~/.gemini/config/plugins/agy-hud` (rechargez ou redémarrez Antigravity si l'icône n'apparaît pas immédiatement) :

```bash
python plugin/install_plugin.py
```

Pour désinstaller :

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Fenêtre flottante autonome et CLI

Fonctionne de manière totalement indépendante sans modifier la configuration des plugins d'Antigravity :

- **Windows (sans fenêtre de console)** : double-cliquez sur `desktop/launch.bat` ou `desktop/launch.pyw`
- **Interface Python / CLI** :

```bash
# Lancer la fenêtre flottante (par défaut : EN, rafraîchissement 500 ms, opacité 92 %)
python -m desktop.cli

# Options disponibles : --lang en|zh, --refresh-ms 500, --alpha 0.92
python -m desktop.cli --lang zh --refresh-ms 1000

# Afficher un instantané unique dans le terminal et quitter
python -m desktop.cli --cli

# Afficher une ligne récapitulative à chaque nouveau tour terminé (--interval par défaut : 1.0 s)
python -m desktop.cli --watch --interval 1.0
```

> [!TIP]
> Faites un glisser-déposer avec le bouton gauche sur la barre supérieure pour déplacer la fenêtre (sauf si la position est verrouillée), cliquez sur `▾` ou double-cliquez sur le texte pour déplier/replier les détails, et faites un **clic droit** n'importe où pour régler la **Langue (`EN` / `中文`)**, **Toujours au premier plan**, **Fixer la position**, l'**Opacité (`100%`–`50%`)** ou la **Fréquence de rafraîchissement (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Champs de données

AGY-HUD lit `gen_metadata` et `steps` depuis `~/.gemini/antigravity/conversations/<uuid>.db` :

| Chemin du champ | Donnée lue | Solution de repli |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | **Identifiant réel du modèle routé** (ex. `gemini-3.8-flash-k`) | Nom affiché dans l'UI (`f1.f21`) |
| `gen_metadata.f1.f4` | Cache (`f5`), nouvelle entrée (`f2`), sortie (`f3` ou `f1`), réflexion (`f9`), visible (`f10`) | Ancien format (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Utilisation actuelle du contexte (`f1`) et limite de fenêtre (`f4`, ex. `256,000`) | `cache + nouvelle entrée` ; table de limites par modèle |
| `gen_metadata.f1.f11` / `f1.f12` | Délai jusqu'au premier token (`TTFT`, `f11`) et durée de streaming (`f12`) | `0.0s` |
| `steps` (`status != 3`) | Temps écoulé de l'étape de génération active (`step_type = 15`) ; le plugin affiche aussi `TOOL` sur les autres étapes actives et associe les horodatages via `f1.f20` | État inactif |

---

## Structure du projet

```text
agy-hud/
├── desktop/                     # Fenêtre flottante et CLI en Python 3.9+ standard
│   ├── telemetry.py             # Lecteur SQLite (?mode=ro) + WAL et décodeur protobuf
│   ├── hud_pill.py              # Fenêtre Tkinter sans bordure, carte et interface EN/中文
│   ├── cli.py                   # Point d'entrée GUI / --cli / --watch
│   ├── launch.pyw               # Lanceur silencieux en arrière-plan pour Windows
│   └── launch.bat               # Script de lancement par double-clic sous Windows
├── plugin/                      # Plugin de panneau latéral pour Antigravity 2.0
│   ├── plugin.json              # Manifeste du plugin
│   ├── install_plugin.py        # Script d'installation / désinstallation
│   ├── assets/logo.svg          # Icône du plugin
│   └── sidecars/hud_panel/      # Backend node:sqlite (sondage 450 ms, ETag) et UI Webview
├── docs/
│   └── assets/                  # Bannière SVG et visuels d'aperçu
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Licence

Distribué sous [MIT License](LICENSE).
