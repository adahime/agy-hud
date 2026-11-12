<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD 横幅" width="100%" />

<p>
  <strong>适用于 Google Antigravity 的实时生成速度、TTFT、当前模型与上下文用量监控工具</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="MIT 许可证" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ 标准库" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js 内置 SQLite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="零第三方依赖" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="8 种语言文档" />
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
  <a href="#overview">功能介绍</a> ·
  <a href="#quick-start">快速开始</a> ·
  <a href="#protobuf-map">数据字段说明</a> ·
  <a href="CHANGELOG.md">更新日志</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="AGY-HUD 桌面悬浮窗与侧边栏插件预览" width="100%" />
</div>

---

## <a id="overview"></a>功能介绍

**AGY-HUD** 是一款轻量级的 Google Antigravity 桌面悬浮监控窗、命令行工具与原生侧边栏插件。它以只读模式（`?mode=ro`）直接读取本地 SQLite 对话数据库，无需配置 API 代理或抓包，即可实时显示生成速度、首字延迟（`TTFT`）、当前使用的模型名称以及上下文窗口占用情况。

### 主要特性

- **只读读取本地数据**：以只读模式（`?mode=ro`）解析 `~/.gemini/antigravity/conversations/<uuid>.db`，无需填写 API 密钥，也不拦截网络请求。
- **生成速度与端到端速度**：同时计算首字之后的流式生成速度（`GEN TPS = 输出 Token / 流式耗时`）以及计入首字延迟后的整体速度（`E2E TPS = 输出 Token / (TTFT + 流式耗时)`）。对于耗时低于 500 毫秒的瞬时缓冲输出，会单独标记为 `BUF`，避免瞬时极值影响峰值统计。
- **准确的模型与上下文上限识别**：直接读取记录中的模型标识字段 `f19`（例如 `gemini-3.8-flash-k`）与真实上下文上限 `f9.f10.f4`（例如 `256,000`）。
- **零第三方依赖**：桌面悬浮窗与命令行工具仅使用 Python 标准库（`sqlite3`、`tkinter`），侧边栏插件仅使用 Node.js 内置的 `node:sqlite`，无需执行 `pip install` 或 `npm install`。
- **英文与中文界面切换**：默认采用简洁的英文指标缩写（如 `GEN`、`E2E`、`STR`、`BUF`、`TTFT`、`THK`、`OUT`、`CTX`），支持在右键菜单或插件右上角随时切换中英文显示。

---

## <a id="quick-start"></a>快速开始

### 1. Antigravity 2.0 侧边栏插件

安装到 `~/.gemini/config/plugins/agy-hud`，在 Antigravity 侧边栏中查看实时速率柱状图与近期请求明细（自动适配浅色与深色主题）：

```bash
python plugin/install_plugin.py
```

卸载插件：

```bash
python plugin/install_plugin.py --uninstall
```

### 2. 独立桌面悬浮窗与命令行工具

完全独立运行，不会改动 Antigravity 的任何现有插件配置：

- **Windows 桌面直接启动（不弹出控制台窗口）**：双击运行 `desktop/launch.bat` 或 `desktop/launch.pyw`
- **Python 图形界面 / 命令行**：

```bash
# 启动桌面悬浮窗（默认英文界面，每 500ms 刷新一次）
python -m desktop.cli

# 在终端输出一次当前状态
python -m desktop.cli --cli

# 在终端中持续刷新显示
python -m desktop.cli --watch
```

> [!TIP]
> 在桌面悬浮窗任意位置**点击鼠标右键**，即可调整**显示语言（`EN` / `中文`）**、**窗口置顶**、**锁定位置**、**窗口透明度（`100%`–`50%`）**以及**刷新间隔（`0.5s`–`5s`）**。

---

## <a id="protobuf-map"></a>数据字段说明

AGY-HUD 从 `~/.gemini/antigravity/conversations/<uuid>.db` 中读取以下生成记录字段：

| 字段路径 | 对应数据 | 备选回退 |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | 检测到的模型标识（如 `gemini-3.8-flash-k`） | 展示名称（`f1.f21`） |
| `gen_metadata.f1.f4` | 缓存（`f5`）、新输入（`f2`）、输出（`f3`）、思考（`f9`）、正文（`f10`） | 旧版统计字段（`f1.f17.f2`） |
| `gen_metadata.f1.f9.f10` | 当前上下文用量（`f1`）与窗口上限（`f4`，如 `256,000`） | 模型上限对照表 |
| `gen_metadata.f1.f11` / `f12` | 首字延迟（`TTFT`）与流式生成持续时间 | `0.0s` |
| `steps`（最新活跃记录） | 当前生成步骤（`step_type = 15`）已运行时间 | 空闲状态 |

---

## 项目目录结构

```text
agy-hud/
├── desktop/                     # 桌面悬浮窗与命令行工具（纯 Python 标准库）
│   ├── telemetry.py             # 只读 SQLite + WAL 与 protobuf 解析模块
│   ├── hud_pill.py              # Tkinter 悬浮胶囊与展开卡片界面
│   ├── cli.py                   # 图形界面 / --cli / --watch 统一入口
│   ├── launch.pyw               # Windows 后台静默启动脚本
│   └── launch.bat               # Windows 双击启动脚本
├── plugin/                      # Antigravity 2.0 侧边栏插件
│   ├── plugin.json              # 插件清单文件
│   ├── install_plugin.py        # 安装 / 卸载脚本
│   ├── assets/logo.svg          # 插件图标
│   └── sidecars/hud_panel/      # node:sqlite 后端与网页视图界面
├── docs/
│   └── assets/                  # SVG 横幅与界面预览图
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## 开源协议

基于 [MIT License](LICENSE) 开源。
