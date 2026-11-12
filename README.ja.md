<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD バナー" width="100%" />

<p>
  <strong>Google Antigravity 向けのリアルタイム生成速度・TTFT・実ルーティング先モデル ID・コンテキスト使用量モニター</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="ライセンス: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ 標準ライブラリ" />
  <img src="https://img.shields.io/badge/Node.js-22.5%2B%20node%3Asqlite-06b6d4?style=flat-square" alt="Node.js 22.5+ node:sqlite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20External-10b981?style=flat-square" alt="外部パッケージ不要" />
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
  <a href="#quick-start">使い方</a> ·
  <a href="#protobuf-map">データ項目</a> ·
  <a href="CHANGELOG.md">変更履歴</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="AGY-HUD デスクトップウィンドウとサイドパネルのプレビュー" width="100%" />
</div>

---

## <a id="overview"></a>概要

**AGY-HUD** は、Google Antigravity 向けの軽量なデスクトップ常駐モニター、CLI ツール、およびサイドパネルプラグインです。ローカルの SQLite 会話データベース（`~/.gemini/antigravity/conversations/<uuid>.db` および `-wal`）を読み取り専用モードで直接参照し、API プロキシや通信傍受を行わずに、生成速度、初回トークンまでの待ち時間（`TTFT`）、**実際にルーティングされたバックエンドのモデル ID**、コンテキスト使用量を表示します。

### 主な特徴

- **実ルーティング先のモデル ID を優先表示**：画面表示用のラベル（`f21`）ではなく、実際にバックエンドへルーティングされたモデル識別子 `f19`（例：`gemini-3.8-flash-k`）を優先して読み取ります（`f21` は `f19` が空の場合のフォールバックとして使用）。また、記録されたコンテキスト上限 `f9.f10.f4`（例：`256,000`）もそのまま取得します。
- **生成速度と全体速度の計測**：初回トークン以降のストリーミング速度（`GEN TPS = 出力トークン数 / ストリーム時間`）と、`TTFT` を含めたエンドツーエンド速度（`E2E TPS = 出力トークン数 / (TTFT + ストリーム時間)`）の両方を計測します。ストリーム時間が `0.5s` 未満（または `1.0s` 未満かつ `1,200 tok/s` 超）の短時間バッファ応答は `BUF` と判定して `PEAK TPS` の集計から除外し、`E2E` 速度および直前の継続ストリーミング速度（`STR`）を表示します。
- **読み取り専用のローカルデータベース参照**：Python デスクトップ版および CLI は SQLite URI `?mode=ro` で接続して `.db` と `.db-wal` の更新時刻を監視し、サイドパネルプラグインは Node.js 組み込みの `node:sqlite` を `{ readOnly: true }` で開きます。API キーやプロキシ設定は不要です。
- **外部パッケージ不要**：デスクトップウィンドウと CLI は Python 3.9+ 標準ライブラリ（`sqlite3`、`tkinter`）のみで動作し、サイドパネルプラグインは Antigravity 同梱の `sidecar_sdk` と Node.js 22.5+ 組み込みの `node:sqlite` を使用します。`pip install` や `npm install` は不要です。
- **デスクトップピル・CLI・サイドパネルプラグイン**：サイドパネルは IDE のライト／ダークテーマに自動追従し、`Auto Pane`・`Latest DB`・直近 15 件の会話から表示対象を切り替えられ、直近 28 回の棒グラフと直近 30 件の呼び出し履歴を表示します。デスクトップ版・プラグイン版ともに既定では短い英語略称（`GEN`、`E2E`、`STR`、`BUF`、`TTFT`、`THK`、`OUT`、`CTX`）を表示し、`EN` と `中文` をいつでも切り替えられます。

---

## <a id="quick-start"></a>使い方

### 1. Antigravity 2.0 サイドパネルプラグイン

`~/.gemini/config/plugins/agy-hud` にインストールします（アイコンがすぐに出ない場合は Antigravity を再読み込み／再起動してください）：

```bash
python plugin/install_plugin.py
```

アンインストールする場合：

```bash
python plugin/install_plugin.py --uninstall
```

### 2. スタンドアロン・デスクトップウィンドウ & CLI

Antigravity の既存プラグイン設定を変更せず、単体で動作します：

- **Windows デスクトップ（コマンド画面なしで起動）**：`desktop/launch.bat` または `desktop/launch.pyw` をダブルクリック
- **Python GUI / CLI**：

```bash
# デスクトップ常駐ウィンドウを起動（既定：英語、500ms 間隔、不透明度 92%）
python -m desktop.cli

# オプション指定例：--lang en|zh, --refresh-ms 500, --alpha 0.92
python -m desktop.cli --lang zh --refresh-ms 1000

# ターミナルに現在の状態を 1 回だけ出力して終了
python -m desktop.cli --cli

# 新しいターン完了ごとに 1 行サマリーを出力（--interval 既定値は 1.0 秒）
python -m desktop.cli --watch --interval 1.0
```

> [!TIP]
> ウィンドウ上部を左ドラッグして移動（位置固定時は無効）、`▾` をクリックまたはテキストをダブルクリックして詳細を展開／折りたたみ、任意の場所を**右クリック**して**表示言語（`EN` / `中文`）**、**最前面表示**、**位置固定**、**透明度（`100%`–`50%`）**、**更新間隔（`0.5s`–`5s`）**を変更できます。

---

## <a id="protobuf-map"></a>データ項目

AGY-HUD は `~/.gemini/antigravity/conversations/<uuid>.db` の `gen_metadata` と `steps` から以下のデータを読み取ります：

| フィールドパス | 取得内容 | フォールバック |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | **実ルーティング先のバックエンドモデル識別子**（例：`gemini-3.8-flash-k`） | UI 表示名（`f1.f21`） |
| `gen_metadata.f1.f4` | キャッシュ（`f5`）、新規入力（`f2`）、出力（`f3` または `f1`）、思考（`f9`）、本文出力（`f10`） | 旧形式カウント（`f1.f17.f2`） |
| `gen_metadata.f1.f9.f10` | 現在のコンテキスト量（`f1`）とウィンドウ上限（`f4`、例：`256,000`） | `キャッシュ + 新規入力`、モデル別上限テーブル |
| `gen_metadata.f1.f11` / `f1.f12` | 初回トークン遅延（`TTFT`、`f11`）とストリーミング生成時間（`f12`） | `0.0s` |
| `steps`（`status != 3`） | 実行中モデル生成（`step_type = 15`）の経過時間（プラグインは他の実行中ステップで `TOOL` 表示および `f1.f20` による時刻取得にも対応） | 待機状態 |

---

## ディレクトリ構成

```text
agy-hud/
├── desktop/                     # Python 3.9+ 標準ライブラリ製の常駐ウィンドウ & CLI
│   ├── telemetry.py             # 読み取り専用 SQLite (?mode=ro) + WAL・protobuf パーサー
│   ├── hud_pill.py              # Tkinter フレームレスウィンドウ・カード・EN/中文 UI
│   ├── cli.py                   # GUI / --cli / --watch エントリポイント
│   ├── launch.pyw               # Windows サイレント GUI ランチャー
│   └── launch.bat               # Windows ダブルクリック用バッチファイル
├── plugin/                      # Antigravity 2.0 サイドパネルプラグイン
│   ├── plugin.json              # プラグイン定義ファイル
│   ├── install_plugin.py        # インストール／アンインストール用スクリプト
│   ├── assets/logo.svg          # プラグインアイコン
│   └── sidecars/hud_panel/      # node:sqlite バックエンド（450ms 監視・ETag）と UI
├── docs/
│   └── assets/                  # バナーとプレビュー用の SVG 画像
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## ライセンス

[MIT License](LICENSE) の下で公開されています。
