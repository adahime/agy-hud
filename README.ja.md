<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD バナー" width="100%" />

<p>
  <strong>Google Antigravity 向けリアルタイム Token/s・TTFT・生モデル ID・コンテキストウィンドウ HUD</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="ライセンス: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ 標準ライブラリ" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js 組み込み SQLite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="依存関係ゼロ" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="8言語ドキュメント" />
</p>

<p>
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <strong>日本語</strong> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ru.md">Русский</a>
</p>

<p>
  <a href="#overview">概要</a> ·
  <a href="#quick-start">クイックスタート</a> ·
  <a href="#protobuf-map">Protobuf マップ</a> ·
  <a href="CHANGELOG.md">変更履歴</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="AGY-HUD デスクトップピルとネイティブサイドペインのプレビュー" width="100%" />
</div>

---

## <a id="overview"></a>AGY-HUD とは？

多くのトークン計測ツールは API 通信をプロキシしたり、クライアント側のトークナイザでサイズを推定したりします。**AGY-HUD** は Google Antigravity のローカル SQLite + WAL 会話データベースを厳格な読み取り専用モード（`?mode=ro`）で直接参照し、ディスク上のワイヤ形式 protobuf `gen_metadata` および `steps` レコードをデコードします。

| 主な機能 | 詳細 |
| :--- | :--- |
| **デュアル TPS 計測** | 純粋なストリーミング速度（`GEN TPS = output / stream_sec`）と、初回トークン遅延を含む体感エンドツーエンド速度（`E2E TPS = output / (ttft + stream_sec)`）を同時に計測します。 |
| **バッファバースト保護** | ミリ秒単位の単一パケット送信（`BUF < 500ms`）を自動検知してフラグ付けし、`100,000+ tok/s` のような擬似スパイクが `PEAK TPS` やグラフを歪めるのを防ぎます。 |
| **生モデル ID の優先取得** | protobuf の `f19` フィールド（例：`GEMINI-3.8-FLASH-K`）と実際のコンテキスト上限 `f9.f10.f4`（例：`256,000`）を優先的に読み取ります。 |
| **外部依存ゼロ** | デスクトップフローティングピルと CLI は Python 標準ライブラリ（`sqlite3`、`tkinter`）のみで動作し、サイドペインプラグインは Node.js 組み込みの `node:sqlite` を使用します。 |
| **EN / 中文 ライブ切替 UI** | デフォルトはコンパクトな英語略称（`GEN`、`E2E`、`STR`、`BUF`、`TTFT`、`THK`、`OUT`、`CTX`）を採用し、`EN / 中文` の即時切り替えにも対応しています。 |

---

## <a id="quick-start"></a>クイックスタート

### 1. Antigravity 2.0 ネイティブ・サイドペインプラグイン

`~/.gemini/config/plugins/agy-hud` にインストールされ、ライト／ダークテーマ自動連動、TPS 棒グラフ、呼び出しログを備えた補助サイドペインとして動作します：

```bash
python plugin/install_plugin.py
```

アンインストールする場合：

```bash
python plugin/install_plugin.py --uninstall
```

### 2. スタンドアロン・デスクトップピル & CLI

Antigravity のプラグイン設定を一切変更せず、完全に独立して実行できます：

- **Windows GUI（コンソール非表示）**：`desktop/launch.bat` または `desktop/launch.pyw` をダブルクリック
- **Python GUI / CLI**：

```bash
# フローティング HUD ピルを起動（デフォルト：EN、500ms 更新）
python -m desktop.cli

# ターミナルへ 1 回スナップショット出力
python -m desktop.cli --cli

# ターミナルでリアルタイム監視
python -m desktop.cli --watch
```

> [!TIP]
> フローティングピル上の任意の場所を**右クリック**すると、**言語（`EN` / `中文`）**、**最前面固定（Always on Top）**、**位置固定**、**不透明度（`100%`–`50%`）**、**更新間隔（`0.5s`–`5s`）** を切り替えられます。

---

## <a id="protobuf-map"></a>Protobuf テレメトリマップ

AGY-HUD は `~/.gemini/antigravity/conversations/<uuid>.db` から一次生成メトリクスを抽出します：

| フィールドパス | 抽出メトリクス | フォールバック |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | 生の検出モデル識別子（`gemini-3.8-flash-k`） | `f1.f21` 表示名 |
| `gen_metadata.f1.f4` | `f5` キャッシュ、`f2` 新規入力、`f3` 出力、`f9` 思考、`f10` 可視出力 | `f1.f17.f2` レガシー集計 |
| `gen_metadata.f1.f9.f10` | `f1` 有効コンテキスト量、`f4` ウィンドウ上限（`256,000`） | モデル別上限テーブル |
| `gen_metadata.f1.f11` / `f12` | `TTFT` およびストリーミング生成 `Duration` | `0.0s` |
| `steps`（最新の非終了ステップ） | 実行中プランナーステップ（`step_type = 15`）の経過時間 | アイドル状態 |

---

## リポジトリ構成

```text
agy-hud/
├── desktop/                     # 依存関係ゼロの Python デスクトップピル & CLI
│   ├── telemetry.py             # 読み取り専用 SQLite+WAL & protobuf デコーダ
│   ├── hud_pill.py              # フレームレス Tkinter ピル & EN/中文カード UI
│   ├── cli.py                   # GUI / --cli / --watch エントリポイント
│   ├── launch.pyw               # Windows サイレント GUI ランチャー
│   └── launch.bat               # Windows ダブルクリック用ランチャー
├── plugin/                      # Antigravity 2.0 ネイティブサイドペイン UI プラグイン
│   ├── plugin.json              # Antigravity プラグインマニフェスト
│   ├── install_plugin.py        # ワンコマンドインストーラ／アンインストーラ
│   ├── assets/logo.svg          # ベクターダイヤルアイコン
│   └── sidecars/hud_panel/      # node:sqlite バックエンド & Webview ダッシュボード
├── docs/
│   └── assets/                  # SVG バナー & UI プレビュー画像
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## ライセンス

[MIT License](LICENSE) の下で公開されています。
