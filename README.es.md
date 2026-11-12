<div align="center">

<img src="docs/assets/banner.svg" alt="Banner de AGY-HUD" width="100%" />

<p>
  <strong>Monitor HUD en tiempo real de Token/s, TTFT, ID de modelo bruto y ventana de contexto para Google Antigravity</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="Licencia: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ Stdlib" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js SQLite integrado" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="Cero dependencias" />
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
  <a href="#overview">Resumen</a> ·
  <a href="#quick-start">Inicio rápido</a> ·
  <a href="#protobuf-map">Mapa Protobuf</a> ·
  <a href="CHANGELOG.md">Historial de cambios</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="Vista previa de la cápsula de escritorio y el panel lateral nativo de AGY-HUD" width="100%" />
</div>

---

## <a id="overview"></a>¿Por qué AGY-HUD?

La mayoría de los contadores de tokens actúan como proxy de tu tráfico API o estiman tamaños mediante tokenizadores locales. **AGY-HUD** lee directamente las bases de datos de conversación SQLite + WAL de Google Antigravity en estricto modo de solo lectura (`?mode=ro`) y decodifica en tiempo real los registros binarios protobuf `gen_metadata` y `steps` almacenados en disco.

| Capacidad | Detalles |
| :--- | :--- |
| **Métricas Duales de TPS** | Mide tanto la velocidad pura de transmisión (`GEN TPS = output / stream_sec`) como la velocidad percibida de extremo a extremo (`E2E TPS = output / (ttft + stream_sec)`). |
| **Protección contra Ráfagas en Búfer** | Marca automáticamente las entregas instantáneas en un único paquete (`BUF < 500ms`) para que los picos artificiales de `100,000+ tok/s` no distorsionen el `PEAK TPS` ni las gráficas. |
| **Prioridad al ID Bruto del Modelo** | Lee directamente el campo protobuf `f19` (por ejemplo, `GEMINI-3.8-FLASH-K`) junto con el límite real de ventana de contexto `f9.f10.f4` (por ejemplo, `256,000`). |
| **Cero Dependencias** | La cápsula flotante de escritorio y la CLI dependen exclusivamente de la biblioteca estándar de Python (`sqlite3`, `tkinter`); el complemento lateral usa `node:sqlite` integrado en Node.js. |
| **Cambio de UI EN / 中文 en Vivo** | Utiliza por defecto abreviaturas técnicas compactas en inglés (`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`), con cambio instantáneo `EN / 中文`. |

---

## <a id="quick-start"></a>Inicio rápido

### 1. Complemento Nativo de Panel Lateral para Antigravity 2.0

Se instala en `~/.gemini/config/plugins/agy-hud` como vista auxiliar del panel lateral con sincronización automática de tema claro/oscuro, gráfico de barras TPS y registro de llamadas:

```bash
python plugin/install_plugin.py
```

Para desinstalar:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. Cápsula Flotante de Escritorio Independiente y CLI

Funciona de manera totalmente independiente sin modificar los complementos de Antigravity:

- **GUI de Windows (sin ventana de consola)**: haz doble clic en `desktop/launch.bat` o `desktop/launch.pyw`
- **Python GUI / CLI**:

```bash
# Cápsula HUD flotante (por defecto: EN, actualización cada 500 ms)
python -m desktop.cli

# Captura instantánea única en terminal
python -m desktop.cli --cli

# Monitorización continua en terminal
python -m desktop.cli --watch
```

> [!TIP]
> Haz **clic derecho** en cualquier parte de la cápsula flotante para cambiar el **Idioma (`EN` / `中文`)**, **Siempre visible**, **Fijar posición**, **Opacidad (`100%`–`50%`)** o **Frecuencia de actualización (`0.5s`–`5s`)**.

---

## <a id="protobuf-map"></a>Mapa de Telemetría Protobuf

AGY-HUD extrae métricas reales de generación directamente desde `~/.gemini/antigravity/conversations/<uuid>.db`:

| Ruta del campo | Métrica extraída | Alternativa |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | Identificador bruto del modelo detectado (`gemini-3.8-flash-k`) | Nombre visible `f1.f21` |
| `gen_metadata.f1.f4` | `f5` caché, `f2` entrada nueva, `f3` salida, `f9` razonamiento, `f10` visible | Conteo heredado `f1.f17.f2` |
| `gen_metadata.f1.f9.f10` | `f1` tamaño de contexto activo, `f4` límite de ventana (`256,000`) | Tabla de límites por modelo |
| `gen_metadata.f1.f11` / `f12` | `TTFT` y duración de transmisión `Duration` | `0.0s` |
| `steps` (último no terminal) | Tiempo transcurrido del paso activo del planificador (`step_type = 15`) | Estado inactivo |

---

## Estructura del Repositorio

```text
agy-hud/
├── desktop/                     # Cápsula de escritorio y CLI en Python sin dependencias
│   ├── telemetry.py             # Decodificador SQLite+WAL solo lectura y protobuf
│   ├── hud_pill.py              # Cápsula Tkinter sin bordes y tarjeta EN/中文
│   ├── cli.py                   # Punto de entrada GUI / --cli / --watch
│   ├── launch.pyw               # Lanzador GUI silencioso para Windows
│   └── launch.bat               # Lanzador con doble clic para Windows
├── plugin/                      # Complemento nativo de panel lateral para Antigravity 2.0
│   ├── plugin.json              # Manifiesto del complemento Antigravity
│   ├── install_plugin.py        # Instalador / desinstalador en un comando
│   ├── assets/logo.svg          # Emblema vectorial del dial
│   └── sidecars/hud_panel/      # Backend node:sqlite y panel Webview
├── docs/
│   └── assets/                  # Banner SVG y gráficos de vista previa
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## Licencia

Publicado bajo la [MIT License](LICENSE).
