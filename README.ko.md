<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD 배너" width="100%" />

<p>
  <strong>Google Antigravity용 실시간 토큰 속도, TTFT, 실제 라우팅 모델 ID 및 컨텍스트 사용량 모니터</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="라이선스: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ 표준 라이브러리" />
  <img src="https://img.shields.io/badge/Node.js-22.5%2B%20node%3Asqlite-06b6d4?style=flat-square" alt="Node.js 22.5+ node:sqlite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20External-10b981?style=flat-square" alt="외부 패키지 없음" />
  <img src="https://img.shields.io/badge/UI-EN%20%2F%20%E4%B8%AD%E6%96%87-6366f1?style=flat-square" alt="EN / 中文" />
  <img src="https://img.shields.io/badge/Docs-8%20Languages-ec4899?style=flat-square" alt="8개 언어 문서" />
</p>

<p>
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <strong>한국어</strong> ·
  <a href="README.es.md">Español</a> ·
  <a href="README.fr.md">Français</a> ·
  <a href="README.de.md">Deutsch</a> ·
  <a href="README.ru.md">Русский</a>
</p>

<p>
  <a href="#overview">개요</a> ·
  <a href="#quick-start">빠른 시작</a> ·
  <a href="#protobuf-map">데이터 필드</a> ·
  <a href="CHANGELOG.md">변경 이력</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="AGY-HUD 데스크톱 창 및 사이드 패널 미리보기" width="100%" />
</div>

---

## <a id="overview"></a>개요

**AGY-HUD**는 Google Antigravity용 경량 데스크톱 플로팅 모니터, CLI 도구 및 사이드 패널 플러그인입니다. 로컬 SQLite 대화 데이터베이스(`~/.gemini/antigravity/conversations/<uuid>.db` 및 `-wal`)를 읽기 전용으로 직접 조회하여, API 프록시나 네트워크 가로채기 없이 토큰 생성 속도, 첫 토큰 지연 시간(`TTFT`), **실제로 라우팅된 백엔드 모델 ID**, 컨텍스트 사용량을 실시간으로 표시합니다.

### 주요 기능

- **실제 라우팅 모델 ID 우선 표시**: 화면 표시 이름(`f21`)이 아니라 실제로 백엔드에 라우팅된 모델 식별자 필드 `f19`(예: `gemini-3.8-flash-k`)를 우선적으로 읽어옵니다(`f21`은 `f19`가 비어 있을 때만 대체용으로 사용). 또한 기록에 보고된 컨텍스트 한도 `f9.f10.f4`(예: `256,000`)를 직접 반영합니다.
- **생성 속도 및 전체 응답 속도 측정**: 첫 토큰 이후 스트리밍 속도(`GEN TPS = 출력 토큰 / 스트림 시간`)와 `TTFT`를 포함한 종단 간 속도(`E2E TPS = 출력 토큰 / (TTFT + 스트림 시간)`)를 함께 계산합니다. 스트림 시간이 `0.5s` 미만이거나 `1.0s` 미만이면서 `1,200 tok/s`를 넘는 버퍼 응답은 `BUF`로 표시하여 `PEAK TPS` 집계에서 제외하고 `E2E` 속도와 이전 지속 스트리밍 속도(`STR`)로 표시합니다.
- **읽기 전용 로컬 데이터베이스 접근**: Python 데스크톱 앱과 CLI는 SQLite URI `?mode=ro`로 연결해 `.db` 및 `.db-wal` 수정 시간을 추적하며, Antigravity 사이드 패널 플러그인은 Node.js 내장 `node:sqlite`를 `{ readOnly: true }` 옵션으로 엽니다. API 키나 네트워크 프록시 설정이 필요 없습니다.
- **외부 패키지 불필요**: 데스크톱 창과 CLI는 Python 3.9+ 표준 라이브러리(`sqlite3`, `tkinter`)만 사용하며, 사이드 패널 플러그인은 Antigravity에 포함된 `sidecar_sdk`와 Node.js 22.5+ 내장 `node:sqlite`를 사용합니다. `pip install`이나 `npm install`이 필요하지 않습니다.
- **데스크톱 창, CLI 및 사이드 패널 플러그인**: 사이드 패널은 IDE 라이트/다크 테마에 자동 동기화되며 `Auto Pane`, `Latest DB` 또는 최근 15개 대화 중 하나를 선택할 수 있고, 최근 28회 막대 차트와 30회 호출 기록을 표시합니다. 데스크톱 창과 플러그인 모두 기본적으로 간결한 영문 약어(`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`)를 사용하며 `EN`과 `中文` 간 전환을 지원합니다.

---

## <a id="quick-start"></a>빠른 시작

### 1. Antigravity 2.0 사이드 패널 플러그인

`~/.gemini/config/plugins/agy-hud`에 설치합니다(아이콘이 바로 보이지 않으면 Antigravity를 다시 로드하거나 재시작하세요):

```bash
python plugin/install_plugin.py
```

제거하려면:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. 독립형 데스크톱 창 & CLI

기존 Antigravity 플러그인 설정을 변경하지 않고 단독으로 실행됩니다:

- **Windows 바탕 화면에서 실행(콘솔 창 없음)**: `desktop/launch.bat` 또는 `desktop/launch.pyw` 더블클릭
- **Python GUI / CLI**:

```bash
# 데스크톱 플로팅 창 실행 (기본: 영어, 500ms 갱신, 투명도 92%)
python -m desktop.cli

# 선택 옵션 예시: --lang en|zh, --refresh-ms 500, --alpha 0.92
python -m desktop.cli --lang zh --refresh-ms 1000

# 터미널에 현재 상태를 한 번만 출력하고 종료
python -m desktop.cli --cli

# 새 턴이 끝날 때마다 요약 한 줄씩 출력 (--interval 기본값 1.0초)
python -m desktop.cli --watch --interval 1.0
```

> [!TIP]
> 창 상단을 왼쪽 드래그해 이동하고(고정 시 이동 불가), `▾` 클릭 또는 텍스트 더블클릭으로 상세 카드를 펼치거나 접을 수 있습니다. 창 아무 곳이나 **오른쪽 클릭**하면 **언어(`EN` / `中文`)**, **항상 위**, **위치 고정**, **투명도(`100%`–`50%`)**, **갱신 주기(`0.5s`–`5s`)**를 설정할 수 있습니다.

---

## <a id="protobuf-map"></a>데이터 필드

AGY-HUD는 `~/.gemini/antigravity/conversations/<uuid>.db`의 `gen_metadata` 및 `steps` 테이블에서 다음 항목을 읽어옵니다:

| 필드 경로 | 읽어오는 데이터 | 대체(폴백) 기준 |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | **실제 라우팅된 백엔드 모델 식별자** (예: `gemini-3.8-flash-k`) | UI 표시 이름 (`f1.f21`) |
| `gen_metadata.f1.f4` | 캐시(`f5`), 새 입력(`f2`), 출력(`f3` 또는 `f1`), 사고(`f9`), 본문 출력(`f10`) | 이전 형식 카운트 (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | 현재 컨텍스트 사용량 (`f1`) 및 윈도우 한도 (`f4`, 예: `256,000`) | `캐시 + 새 입력`, 모델별 한도 테이블 |
| `gen_metadata.f1.f11` / `f1.f12` | 첫 토큰 지연 (`TTFT`, `f11`) 및 스트리밍 생성 시간 (`f12`) | `0.0s` |
| `steps` (`status != 3`) | 실행 중인 생성 단계(`step_type = 15`) 경과 시간(플러그인은 기타 활성 단계의 `TOOL` 상태 및 `f1.f20` 기반 시각 매핑도 지원) | 유휴 상태 |

---

## 프로젝트 구조

```text
agy-hud/
├── desktop/                     # Python 3.9+ 표준 라이브러리 기반 데스크톱 창 & CLI
│   ├── telemetry.py             # 읽기 전용 SQLite (?mode=ro) + WAL 및 protobuf 파서
│   ├── hud_pill.py              # Tkinter 프레임리스 창, 상세 카드 및 EN/中文 UI
│   ├── cli.py                   # GUI / --cli / --watch 진입점
│   ├── launch.pyw               # Windows 백그라운드 GUI 실행 스크립트
│   └── launch.bat               # Windows 더블클릭 배치 파일
├── plugin/                      # Antigravity 2.0 사이드 패널 플러그인
│   ├── plugin.json              # 플러그인 매니페스트
│   ├── install_plugin.py        # 설치 / 제거 스크립트
│   ├── assets/logo.svg          # 플러그인 아이콘
│   └── sidecars/hud_panel/      # node:sqlite 백엔드 (450ms 폴링, ETag) 및 웹뷰 UI
├── docs/
│   └── assets/                  # 배너 및 미리보기용 SVG 이미지
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## 라이선스

[MIT License](LICENSE)를 따릅니다.
