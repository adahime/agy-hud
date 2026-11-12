<div align="center">

<img src="docs/assets/banner.svg" alt="Banner de AGY-HUD" width="100%" />

<p>
  <strong>Monitor en tiempo real de velocidad de tokens, TTFT, identificador real del modelo enrutado y ventana de contexto para Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Licencia: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-22.5%2B%20node%3Asqlite-06b6d4?style=flat-square" alt="Node.js 22.5+ node:sqlite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20External-10b981?style=flat-square" alt="Sin dependencias externas" />
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

**AGY-HUD** es un monitor flotante ligero para escritorio, herramienta CLI y complemento de panel lateral para Google Antigravity. Lee las bases de datos SQLite locales (`~/.gemini/antigravity/conversations/<uuid>.db` y `-wal`) estrictamente en modo de solo lectura para mostrar la velocidad de generación de tokens, la latencia hasta el primer token (`TTFT`), el **identificador real del modelo al que se enrutó la petición** y el uso de la ventana de contexto sin interceptar el tráfico de red.

### Características principales

- **Prioridad al identificador real del modelo enrutado**: Da prioridad al campo protobuf `f19`—el identificador real del modelo en el backend (por ejemplo, `gemini-3.8-flash-k`)—en lugar del nombre visible en la interfaz (`f21`, utilizado solo como alternativa si falta `f19`). También lee el límite real de contexto informado en `f9.f10.f4` (por ejemplo, `256,000`).
- **Velocidad de generación y velocidad total**: Calcula tanto la velocidad de transmisión tras el primer token (`GEN TPS = salida / tiempo_stream`) como la velocidad total incluyendo la espera inicial (`E2E TPS = salida / (TTFT + tiempo_stream)`). Las respuestas completadas en menos de `0.5s` (o en menos de `1.0s` con más de `1,200 tok/s`) se marcan como `BUF`, se excluyen del pico `PEAK TPS` y se muestran con la velocidad `E2E` y la última velocidad sostenida (`STR`).
- **Lectura local en modo solo lectura**: La aplicación de escritorio y la CLI en Python abren la base de datos mediante la URI SQLite `?mode=ro` supervisando cambios en `.db` y `.db-wal`; el complemento lateral usa `node:sqlite` integrado en Node.js (`{ readOnly: true }`). No requiere claves API ni configuración de proxy.
- **Sin paquetes externos**: La ventana de escritorio y la CLI emplean únicamente la biblioteca estándar de Python 3.9+ (`sqlite3`, `tkinter`), y el complemento lateral utiliza el módulo integrado `sidecar_sdk` de Antigravity junto con `node:sqlite` de Node.js 22.5+. No hace falta `pip install` ni `npm install`.
- **Ventana flotante, CLI y panel lateral**: El panel lateral sincroniza automáticamente el tema claro u oscuro, permite elegir entre `Auto Pane`, `Latest DB` o las 15 conversaciones más recientes, y muestra un gráfico de barras de los últimos 28 turnos junto con un historial de 30 llamadas. Tanto el escritorio como el panel muestran por defecto abreviaturas breves en inglés (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`) y permiten cambiar entre `EN` y `中文`.

---

## <a id="quick-start"></a>Inicio rápido

### 1. Complemento de panel lateral para Antigravity 2.0

Instálalo en `~/.gemini/config/plugins/agy-hud` (recarga o reinicia Antigravity si el icono no aparece de inmediato):

```bash
python plugin/install_plugin.py
```

Para desinstalar:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Ventana flotante independiente y CLI

Funciona de forma totalmente independiente sin modificar la configuración de complementos de Antigravity:

- **Windows (sin ventana de consola)**: haz doble clic en `desktop/launch.bat` o `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Abrir ventana flotante en el escritorio (por defecto: EN, refresco cada 500 ms, opacidad 92 %)
python -m desktop.cli

# Opciones disponibles: --lang en|zh, --refresh-ms 500, --alpha 0.92
python -m desktop.cli --lang zh --refresh-ms 1000

# Imprimir una sola instantánea en la terminal y salir
python -m desktop.cli --cli

# Mostrar una línea de resumen cada vez que termina un nuevo turno (--interval por defecto: 1.0 s)
python -m desktop.cli --watch --interval 1.0
```

> [!TIP]
> Arrastra con el botón izquierdo la barra superior para mover la ventana (salvo si está fijada), pulsa `▾` o haz doble clic en el texto para expandir o contraer los detalles, y haz **clic derecho** en cualquier parte para cambiar el **Idioma (`EN` / `中文`)**, **Siempre visible**, **Fijar posición**, **Opacidad (`100%`–`50%`)** o **Frecuencia de actualización (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Campos de datos

AGY-HUD lee `gen_metadata` y `steps` desde `~/.gemini/antigravity/conversations/<uuid>.db`:

| Ruta del campo | Dato extraído | Alternativa |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | **Identificador real del modelo enrutado** (p. ej. `gemini-3.8-flash-k`) | Nombre visible en UI (`f1.f21`) |
| `gen_metadata.f1.f4` | Caché (`f5`), entrada nueva (`f2`), salida (`f3` o `f1`), razonamiento (`f9`), visible (`f10`) | Conteo heredado (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | Uso de contexto actual (`f1`) y límite de ventana (`f4`, p. ej. `256,000`) | `caché + entrada nueva`; tabla de límites por modelo |
| `gen_metadata.f1.f11` / `f1.f12` | Tiempo hasta el primer token (`TTFT`, `f11`) y duración de transmisión (`f12`) | `0.0s` |
| `steps` (`status != 3`) | Tiempo del paso de generación activo (`step_type = 15`); el panel lateral también muestra `TOOL` en otros pasos activos y vincula marcas de tiempo mediante `f1.f20` | Estado inactivo |

---

## Estructura del proyecto

```text
agy-hud/
├── desktop/                     # Ventana flotante y CLI con biblioteca estándar de Python 3.9+
│   ├── telemetry.py             # Lector SQLite (?mode=ro) + WAL y analizador protobuf
│   ├── hud_pill.py              # Ventana flotante Tkinter, tarjeta de detalle e interfaz EN/中文
│   ├── cli.py                   # Punto de entrada para GUI / --cli / --watch
│   ├── launch.pyw               # Lanzador silencioso en segundo plano para Windows
│   └── launch.bat               # Archivo por lotes para abrir con doble clic en Windows
├── plugin/                      # Complemento de panel lateral para Antigravity 2.0
│   ├── plugin.json              # Manifiesto del complemento
│   ├── install_plugin.py        # Script de instalación y desinstalación
│   ├── assets/logo.svg          # Icono del complemento
│   └── sidecars/hud_panel/      # Backend node:sqlite (sondeo 450 ms, ETag) e interfaz web
├── docs/
│   └── assets/                  # Banner SVG y gráficos de vista previa
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Licencia

Publicado bajo la [MIT License](LICENSE).
