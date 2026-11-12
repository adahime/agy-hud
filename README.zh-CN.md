<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD 横幅" width="100%" />

<p>
  <strong>面向 Google Antigravity 的实时 Token/s、TTFT、原始模型 ID 与上下文窗口 HUD 监控工具</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="MIT 许可证" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ 标准库" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js 内置 SQLite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="零外部依赖" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="8 语文档" />
</p>

<p>
  <a href="README.md">English</a> ·
  <strong>简体中文</strong> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ru.md">Русский</a>
</p>

<p>
  <a href="#overview">核心特性</a> ·
  <a href="#quick-start">快速上手</a> ·
  <a href="#protobuf-map">Protobuf 字段映射</a> ·
  <a href="CHANGELOG.md">更新日志</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="AGY-HUD 桌面悬浮球与原生侧边栏效果预览" width="100%" />
</div>

---

## <a id="overview"></a>为什么选择 AGY-HUD？

市面上大多数 Token 统计器需要代理你的 API 流量，或者靠客户端分词器做近似估算。**AGY-HUD** 直接以严格只读模式（`?mode=ro`）读取 Google Antigravity 本地的 SQLite + WAL 对话数据库，并解码磁盘上的二进制 protobuf `gen_metadata` 与 `steps` 记录，拿到最真实的底层耗时与计数数据。

| 核心能力 | 说明 |
| :--- | :--- |
| **双口径 TPS 速率监控** | 同时计算纯流式吐字速度（`GEN TPS = output / stream_sec`）与包含首字延迟（`TTFT`）的端到端速度（`E2E TPS = output / (ttft + stream_sec)`）。 |
| **单包突发脉冲隔离** | 自动识别毫秒级工具回传或缓冲下发（`BUF < 500ms`），避免 `100,000+ tok/s` 假尖峰污染 `PEAK TPS` 与折线图。 |
| **原始模型 ID 优先识别** | 直接优先读取 protobuf `f19` 字段（例如 `GEMINI-3.8-FLASH-K`）以及底层真实上下文窗口上限 `f9.f10.f4`（例如 `256,000`）。 |
| **零外部依赖 & 只读安全** | 桌面悬浮球与 CLI 仅使用 Python 标准库（`sqlite3`、`tkinter`）；Antigravity 原生侧边栏插件仅依赖 Node.js 内置 `node:sqlite`。 |
| **极客英文缩写 / 中文热切换** | 界面默认采用紧凑硬核的英文技术缩写（`GEN`、`E2E`、`STR`、`BUF`、`TTFT`、`THK`、`OUT`、`CTX`），支持随时在 `EN / 中文` 之间切换。 |

---

## <a id="quick-start"></a>快速上手

### 1. Antigravity 2.0 原生侧边栏插件

一键安装到 `~/.gemini/config/plugins/agy-hud`，作为辅助侧边栏视图随主界面启动，支持明暗主题自动同步、TPS 柱状图与调用明细表：

```bash
python plugin/install_plugin.py
```

卸载插件：

```bash
python plugin/install_plugin.py --uninstall
```

### 2. 独立桌面悬浮球与命令行（CLI）

完全独立运行，无需修改或注册任何 Antigravity 插件：

- **Windows 无黑框桌面模式**：直接双击 `desktop/launch.bat` 或 `desktop/launch.pyw`
- **Python GUI / 命令行**：

```bash
# 启动桌面悬浮胶囊（默认：EN，500ms 刷新）
python -m desktop.cli

# 终端单次快照输出
python -m desktop.cli --cli

# 终端持续实时刷屏监控
python -m desktop.cli --watch
```

> [!TIP]
> 在桌面悬浮球任意位置**点击鼠标右键**，即可切换 **语言（`EN` / `中文`）**、**窗口置顶**、**锁定位置**、**透明度（`100%`–`50%`）** 以及 **刷新频率（`0.5s`–`5s`）**。

---

## <a id="protobuf-map"></a>Protobuf 遥测字段映射

AGY-HUD 从 `~/.gemini/antigravity/conversations/<uuid>.db` 中提取第一手生成指标：

| 字段路径 | 提取指标 | 兜底回退 |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | 原始识别模型代号（如 `gemini-3.8-flash-k`） | `f1.f21` 展示名称 |
| `gen_metadata.f1.f4` | `f5` 缓存命中、`f2` 新输入、`f3` 输出、`f9` 思考、`f10` 可见正文 | `f1.f17.f2` 旧版计数 |
| `gen_metadata.f1.f9.f10` | `f1` 当前有效上下文长度、`f4` 窗口总额度（`256,000`） | 模型上下文上限对照表 |
| `gen_metadata.f1.f11` / `f12` | 首字延迟 `TTFT` 与流式生成耗时 `Duration` | `0.0s` |
| `steps`（最新非终态） | 当前活跃规划步骤（`step_type = 15`）实时已用时 | 空闲状态 |

---

## 仓库目录结构

```text
agy-hud/
├── desktop/                     # 零依赖 Python 桌面悬浮球与 CLI
│   ├── telemetry.py             # 只读 SQLite+WAL 与 protobuf 解码器
│   ├── hud_pill.py              # 无边框 Tkinter 悬浮胶囊与 EN/中文卡片界面
│   ├── cli.py                   # GUI / --cli / --watch 统一入口
│   ├── launch.pyw               # Windows 无控制台静默启动脚本
│   └── launch.bat               # Windows 双击批处理启动器
├── plugin/                      # 原生 Antigravity 2.0 侧边栏 UI 插件
│   ├── plugin.json              # Antigravity 插件清单文件
│   ├── install_plugin.py        # 一键安装 / 卸载脚本
│   ├── assets/logo.svg          # 矢量仪表盘图标
│   └── sidecars/hud_panel/      # node:sqlite 后端与 Webview 监控面板
├── docs/
│   └── assets/                  # SVG 顶部横幅与界面预览图
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## 开源许可证

本项目基于 [MIT License](LICENSE) 开源。
