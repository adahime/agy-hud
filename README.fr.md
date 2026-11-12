<div align="center">

<img src="docs/assets/banner.svg" alt="Bannière AGY-HUD" width="100%" />

<p>
  <strong>Moniteur en temps réel de vitesse de tokens, TTFT, modèle actif et fenêtre de contexte pour Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Licence : MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="SQLite intégré dans Node.js" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Sans dépendances externes" />
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

**AGY-HUD** est un moniteur flottant léger pour le bureau, un outil en ligne de commande et un plugin de panneau latéral pour Google Antigravity. Il lit directement les bases SQLite locales en mode lecture seule (`?mode=ro`) afin d'afficher la vitesse de génération, le délai jusqu'au premier token (`TTFT`), le modèle utilisé et l'occupation de la fenêtre de contexte sans relayer le trafic réseau.

### Fonctionnalités principales

- **Lecture locale en lecture seule** : Ouvre `~/.gemini/antigravity/conversations/<uuid>.db` en mode lecture seule (`?mode=ro`). Aucune clé API ni configuration de proxy n'est requise.
- **Vitesse de génération et vitesse globale** : Affiche à la fois la vitesse de diffusion après le premier token (`GEN TPS = sortie / durée_stream`) et la vitesse globale incluant l'attente initiale (`E2E TPS = sortie / (TTFT + durée_stream)`). Les réponses reçues en moins de 500 ms sont marquées `BUF` afin de ne pas fausser les statistiques de pic de vitesse.
- **Identification exacte du modèle et du contexte** : Lit directement l'identifiant du modèle dans `f19` (par exemple `gemini-3.8-flash-k`) et la limite réelle de contexte dans `f9.f10.f4` (par exemple `256,000`).
- **Aucune dépendance externe** : La fenêtre de bureau et l'outil CLI reposent uniquement sur la bibliothèque standard Python (`sqlite3`, `tkinter`), tandis que le plugin latéral utilise le module intégré `node:sqlite`. Aucun `pip install` ni `npm install` n'est nécessaire.
- **Interface en anglais et en chinois** : Utilise par défaut des abréviations anglaises concises (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`), avec bascule entre l'anglais et le chinois via le menu contextuel ou l'en-tête du panneau.

---

## <a id="quick-start"></a>Démarrage rapide

### 1. Plugin de panneau latéral pour Antigravity 2.0

Installez le plugin dans `~/.gemini/config/plugins/agy-hud` pour consulter les graphiques TPS et l'historique récent dans le panneau latéral d'Antigravity (s'adapte automatiquement au thème clair ou sombre) :

```bash
python plugin/install_plugin.py
```

Pour désinstaller :

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Fenêtre flottante autonome et CLI

Fonctionne de manière totalement indépendante sans modifier la configuration des plugins d'Antigravity :

- **Bureau Windows (sans fenêtre de console)** : double-cliquez sur `desktop/launch.bat` ou `desktop/launch.pyw`
- **Interface Python / CLI** :

```bash
# Lancer la fenêtre flottante (par défaut : anglais, rafraîchissement toutes les 500 ms)
python -m desktop.cli

# Afficher un instantané unique dans le terminal
python -m desktop.cli --cli

# Mettre à jour en continu dans le terminal
python -m desktop.cli --watch
```

> [!TIP]
> Faites un **clic droit** n'importe où sur la fenêtre flottante pour modifier la **Langue (`EN` / `中文`)**, **Toujours au premier plan**, **Fixer la position**, l'**Opacité (`100%`–`50%`)** ou la **Fréquence de rafraîchissement (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Champs de données

AGY-HUD lit les données suivantes depuis `~/.gemini/antigravity/conversations/<uuid>.db` :

| Chemin du champ | Donnée lue | Solution de repli |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Identifiant du modèle détecté (`gemini-3.8-flash-k`) | Nom d'affichage (`f1.f21`) |
| `gen_metadata.f1.f4` | Cache (`f5`), nouvelle entrée (`f2`), sortie (`f3`), réflexion (`f9`), visible (`f10`) | Ancien format (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Utilisation actuelle du contexte (`f1`) et limite (`f4`, ex. `256,000`) | Table des limites par modèle |
| `gen_metadata.f1.f11` / `f12` | Délai jusqu'au premier token (`TTFT`) et durée de génération | `0.0s` |
| `steps` (dernière ligne active) | Temps écoulé de l'étape en cours (`step_type = 15`) | État inactif |

---

## Structure du projet

```text
agy-hud/
├── desktop/                     # Fenêtre flottante et CLI avec Python standard
│   ├── telemetry.py             # Lecteur SQLite + WAL en lecture seule et décodeur protobuf
│   ├── hud_pill.py              # Fenêtre flottante Tkinter et carte détaillée
│   ├── cli.py                   # Point d'entrée GUI / --cli / --watch
│   ├── launch.pyw               # Lanceur silencieux en arrière-plan pour Windows
│   └── launch.bat               # Script de lancement par double-clic sous Windows
├── plugin/                      # Plugin de panneau latéral pour Antigravity 2.0
│   ├── plugin.json              # Manifeste du plugin
│   ├── install_plugin.py        # Script d'installation / désinstallation
│   ├── assets/logo.svg          # Icône du plugin
│   └── sidecars/hud_panel/      # Backend node:sqlite et interface Webview
├── docs/
│   └── assets/                  # Bannière SVG et visuels d'aperçu
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Licence

Distribué sous [MIT License](LICENSE).
