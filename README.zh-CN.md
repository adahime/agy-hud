<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD 横幅" width="100%" />

<p>
  <strong>适用于 Google Antigravity 的实时生成速度、TTFT、实际路由模型标识与上下文用量监控工具</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="MIT 许可证" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ 标准库" />
  <img src="https://img.shields.io/badge/Node.js-22.5%2B%20node%3Asqlite-06b6d4?style=flat-square" alt="Node.js 22.5+ node:sqlite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20External-10b981?style=flat-square" alt="零外部依赖" />
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

**AGY-HUD** 是一款轻量级的 Google Antigravity 桌面悬浮监控窗、命令行工具与侧边栏插件。它以只读方式直接读取本地 SQLite 对话数据库（`~/.gemini/antigravity/conversations/<uuid>.db` 及其 `-wal` 日志），无需代理 API 请求或抓包，即可实时显示生成速度、首字延迟（`TTFT`）、**实际路由到的后端模型标识**以及上下文窗口占用情况。

### 主要特性

- **优先读取实际路由模型标识**：读取 `gen_metadata` 中实际路由到的后端模型标识字段 `f19`（例如 `gemini-3.8-flash-k`），而不是只看前端展示名称（`f21` 仅在缺失 `f19` 时作为兜底）；同时读取记录中上报的真实上下文窗口上限 `f9.f10.f4`（例如 `256,000`），仅在缺失时回退到内置模型上限表。
- **生成速度与端到端速度**：同时计算首字之后的流式生成速度（`GEN TPS = 输出 Token / 流式耗时`）以及计入首字延迟后的整体速度（`E2E TPS = 输出 Token / (TTFT + 流式耗时)`）。对于流式耗时低于 `0.5s`（或低于 `1.0s` 且速率超过 `1,200 tok/s`）的瞬时缓冲响应，会标记为 `BUF` 并排除出 `PEAK TPS` 峰值统计，改用 `E2E` 速度与上一轮持续流式速度（`STR`）展示。
- **本地只读数据库访问**：Python 桌面端与命令行工具通过 `?mode=ro` 只读 URI 连接数据库并监控 `.db` 与 `.db-wal` 文件更新时间；Antigravity 侧边栏插件通过 Node.js 内置的 `node:sqlite` 以 `{ readOnly: true }` 模式打开数据库。全程无需填写 API 密钥或配置网络代理。
- **零外部第三方依赖**：桌面悬浮窗与命令行仅使用 Python 3.9+ 标准库（`sqlite3`、`tkinter`），侧边栏插件直接运行在 Antigravity 自带的 `sidecar_sdk` 与 Node.js 22.5+ 内置 `node:sqlite` 上，无需安装任何第三方包（无需 `pip install` 或 `npm install`）。
- **桌面悬浮窗、CLI 与侧边栏插件**：侧边栏面板会自动跟随 IDE 明暗主题，支持切换跟随当前对话（`Auto Pane`）、最新活跃数据库（`Latest DB`）或最近 15 个历史对话，并提供最近 28 次调用的柱状图与最近 30 条调用明细。桌面端与插件端默认采用简洁的英文指标缩写（`GEN`、`E2E`、`STR`、`BUF`、`TTFT`、`THK`、`OUT`、`CTX`），且支持随时切换中英文界面。

---

## <a id="quick-start"></a>快速开始

### 1. Antigravity 2.0 侧边栏插件

一键安装到 `~/.gemini/config/plugins/agy-hud`（若侧边栏图标未立即出现，重新加载或重启 Antigravity 即可）：

```bash
python plugin/install_plugin.py
```

卸载插件：

```bash
python plugin/install_plugin.py --uninstall
```

### 2. 独立桌面悬浮窗与命令行工具

完全独立运行，不会修改 Antigravity 的任何现有插件配置：

- **Windows 桌面直接启动（不弹出控制台窗口）**：双击运行 `desktop/launch.bat` 或 `desktop/launch.pyw`
- **Python 图形界面 / 命令行**：

```bash
# 启动桌面悬浮窗（默认英文界面，500ms 刷新，透明度 92%）
python -m desktop.cli

# 可选参数：--lang en|zh，--refresh-ms 500，--alpha 0.92
python -m desktop.cli --lang zh --refresh-ms 1000

# 在终端输出一次当前状态后退出
python -m desktop.cli --cli

# 在终端中监听变化，每当完成新的一轮调用时输出一行摘要（--interval 默认 1.0 秒）
python -m desktop.cli --watch --interval 1.0
```

> [!TIP]
> 左键按住悬浮窗顶部可拖动位置（锁定后固定），点击 `▾` 或双击标题文字可展开/收起详情卡片；在窗口任意位置**点击鼠标右键**，即可切换**语言（`EN` / `中文`）**、**始终置顶**、**锁定位置**、**透明度（`100%`–`50%`）**与**刷新频率（`0.5s`–`5s`）**。

---

## <a id="protobuf-map"></a>数据字段说明

AGY-HUD 从 `~/.gemini/antigravity/conversations/<uuid>.db` 的 `gen_metadata` 与 `steps` 表中读取以下字段：

| 字段路径 | 对应数据 | 备选回退 |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | **实际路由到的后端模型标识**（如 `gemini-3.8-flash-k`） | 仅作兜底的前端展示名称（`f1.f21`） |
| `gen_metadata.f1.f4` | 缓存（`f5`）、新输入（`f2`）、输出（`f3` 或 `f1`）、思考（`f9`）、可见正文（`f10`） | 旧版统计字段（`f1.f17.f2`） |
| `gen_metadata.f1.f9.f10` | 当前上下文用量（`f1`）与窗口上限（`f4`，如 `256,000`） | `缓存 + 新输入`；内置模型上限表 |
| `gen_metadata.f1.f11` / `f1.f12` | 首字延迟（`TTFT`，`f11`）与流式生成时长（`f12`） | `0.0s` |
| `steps`（`status != 3`） | 进行中生成步骤（`step_type = 15`）已运行时间；侧边栏插件同时显示非生成步骤的 `TOOL` 状态并通过 `f1.f20` 对齐调用时间戳 | 空闲状态 |

---

## 项目目录结构

```text
agy-hud/
├── desktop/                     # Python 3.9+ 标准库桌面悬浮窗与 CLI
│   ├── telemetry.py             # 只读 SQLite (?mode=ro) + WAL 与 protobuf 解析模块
│   ├── hud_pill.py              # Tkinter 无边框悬浮胶囊、详情卡片与 EN/中文界面
│   ├── cli.py                   # 图形界面 / --cli / --watch 统一入口
│   ├── launch.pyw               # Windows 静默后台启动脚本
│   └── launch.bat               # Windows 双击启动脚本
├── plugin/                      # Antigravity 2.0 侧边栏插件
│   ├── plugin.json              # 插件清单文件
│   ├── install_plugin.py        # 安装 / 卸载脚本
│   ├── assets/logo.svg          # 插件图标
│   └── sidecars/hud_panel/      # node:sqlite 后端（450ms 轮询、ETag）与网页界面
├── docs/
│   └── assets/                  # SVG 横幅与界面预览图
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## 开源协议

基于 [MIT License](LICENSE) 开源。
