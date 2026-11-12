<div align="center">

<img src="docs/assets/banner.svg" alt="Banner de AGY-HUD" width="100%" />

<p>
  <strong>Monitor en tiempo real de velocidad de tokens, TTFT, modelo activo y uso de contexto para Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Licencia: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="SQLite integrado en Node.js" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Sin dependencias externas" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="Documentación en 8 idiomas" />
</p>

<p>
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <strong>Español</strong> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ru.md">Русский</a>
</p>

<p>
  <a href="#overview">Descripción</a> ·
  <a href="#quick-start">Inicio rápido</a> ·
  <a href="#protobuf-map">Campos de datos</a> ·
  <a href="CHANGELOG.md">Historial de cambios</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="Vista previa de la ventana flotante y el panel lateral de AGY-HUD" width="100%" />
</div>

---

## <a id="overview"></a>Descripción

**AGY-HUD** es un monitor flotante ligero para escritorio, herramienta CLI y complemento de panel lateral para Google Antigravity. Lee las bases de datos SQLite locales directamente en modo de solo lectura (`?mode=ro`) para mostrar la velocidad de generación de tokens, la latencia hasta el primer token (`TTFT`), el identificador del modelo activo y el uso de la ventana de contexto sin interceptar el tráfico de red.

### Características principales

- **Lectura local en modo solo lectura**: Abre `~/.gemini/antigravity/conversations/<uuid>.db` en modo de solo lectura (`?mode=ro`). No requiere claves API ni configuración de proxy.
- **Velocidad de generación y velocidad total**: Muestra tanto la velocidad de transmisión tras el primer token (`GEN TPS = salida / tiempo_stream`) como la velocidad total incluyendo la espera inicial (`E2E TPS = salida / (TTFT + tiempo_stream)`). Las respuestas entregadas en menos de 500 ms se marcan como `BUF` para que no alteren las estadísticas de velocidad máxima.
- **Identificación precisa del modelo y límite de contexto**: Lee el identificador del modelo desde el campo `f19` (por ejemplo, `gemini-3.8-flash-k`) y el límite real de contexto desde `f9.f10.f4` (por ejemplo, `256,000`).
- **Sin dependencias externas**: La ventana de escritorio y la CLI utilizan únicamente la biblioteca estándar de Python (`sqlite3`, `tkinter`), y el complemento de panel lateral usa el módulo integrado `node:sqlite`. No es necesario ejecutar `pip install` ni `npm install`.
- **Interfaz en inglés y chino**: Muestra abreviaturas breves en inglés por defecto (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) y permite cambiar entre inglés y chino desde el menú contextual o el encabezado del panel.

---

## <a id="quick-start"></a>Inicio rápido

### 1. Complemento de panel lateral para Antigravity 2.0

Instálalo en `~/.gemini/config/plugins/agy-hud` para ver gráficos de TPS y el historial reciente en el panel lateral de Antigravity (se adapta automáticamente al tema claro u oscuro):

```bash
python plugin/install_plugin.py
```

Para desinstalar:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Ventana flotante independiente y CLI

Funciona de forma totalmente independiente sin modificar la configuración de complementos de Antigravity:

- **Escritorio Windows (sin ventana de consola)**: haz doble clic en `desktop/launch.bat` o `desktop/launch.pyw`
- **GUI de Python / CLI**:

```bash
# Abrir ventana flotante en el escritorio (por defecto: inglés, actualización cada 500 ms)
python -m desktop.cli

# Imprimir una sola instantánea en la terminal
python -m desktop.cli --cli

# Actualizar continuamente en la terminal
python -m desktop.cli --watch
```

> [!TIP]
> Haz **clic derecho** en cualquier parte de la ventana flotante para cambiar el **Idioma (`EN` / `中文`)**, **Siempre visible**, **Fijar posición**, **Opacidad (`100%`–`50%`)** o **Intervalo de actualización (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Campos de datos

AGY-HUD lee los siguientes registros de `~/.gemini/antigravity/conversations/<uuid>.db`:

| Ruta del campo | Dato obtenido | Alternativa |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Identificador del modelo detectado (`gemini-3.8-flash-k`) | Nombre visible (`f1.f21`) |
| `gen_metadata.f1.f4` | Caché (`f5`), entrada nueva (`f2`), salida (`f3`), razonamiento (`f9`), visible (`f10`) | Conteo heredado (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Uso actual de contexto (`f1`) y límite (`f4`, p. ej. `256,000`) | Tabla de límites por modelo |
| `gen_metadata.f1.f11` / `f12` | Tiempo hasta el primer token (`TTFT`) y duración de transmisión | `0.0s` |
| `steps` (último registro activo) | Tiempo transcurrido del paso en curso (`step_type = 15`) | Estado inactivo |

---

## Estructura del proyecto

```text
agy-hud/
├── desktop/                     # Ventana flotante y CLI usando Python estándar
│   ├── telemetry.py             # Lector SQLite + WAL en solo lectura y analizador protobuf
│   ├── hud_pill.py              # Ventana flotante en Tkinter y tarjeta de detalles
│   ├── cli.py                   # Punto de entrada para GUI / --cli / --watch
│   ├── launch.pyw               # Lanzador silencioso en segundo plano para Windows
│   └── launch.bat               # Archivo por lotes para abrir con doble clic en Windows
├── plugin/                      # Complemento de panel lateral para Antigravity 2.0
│   ├── plugin.json              # Manifiesto del complemento
│   ├── install_plugin.py        # Script de instalación y desinstalación
│   ├── assets/logo.svg          # Icono del complemento
│   └── sidecars/hud_panel/      # Backend en node:sqlite e interfaz web
├── docs/
│   └── assets/                  # Banner SVG y gráficos de vista previa
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Licencia

Publicado bajo la [MIT License](LICENSE).
