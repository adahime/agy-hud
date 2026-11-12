<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD 배너" width="100%" />

<p>
  <strong>Google Antigravity용 실시간 토큰 속도, TTFT, 사용 모델 및 컨텍스트 사용량 모니터</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="라이선스: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ 표준 라이브러리" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js 내장 SQLite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="외부 의존성 없음" />
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

**AGY-HUD**는 Google Antigravity용 경량 데스크톱 플로팅 모니터, CLI 도구 및 사이드 패널 플러그인입니다. 로컬 SQLite 대화 데이터베이스를 읽기 전용 모드(`?mode=ro`)로 직접 조회하여, API 프록시나 네트워크 가로채기 없이 생성 속도, 첫 토큰 지연 시간(`TTFT`), 사용 중인 모델 ID, 컨텍스트 사용량을 실시간으로 표시합니다.

### 주요 기능

- **읽기 전용 로컬 데이터 조회**: `~/.gemini/antigravity/conversations/<uuid>.db`를 읽기 전용(`?mode=ro`)으로 엽니다. API 키 입력이나 프록시 설정이 필요 없습니다.
- **생성 속도 및 종단 간 속도 측정**: 첫 토큰 이후의 스트리밍 속도(`GEN TPS = 출력 토큰 / 스트림 시간`)와 `TTFT`를 포함한 전체 응답 속도(`E2E TPS = 출력 토큰 / (TTFT + 스트림 시간)`)를 함께 계산합니다. 500밀리초 미만의 짧은 버퍼 응답은 `BUF`로 별도 표시해 최고 속도 통계가 왜곡되지 않도록 합니다.
- **정확한 모델 및 컨텍스트 한도 인식**: 기록에 저장된 모델 식별자 `f19`(예: `gemini-3.8-flash-k`)와 실제 컨텍스트 한도 `f9.f10.f4`(예: `256,000`)를 직접 읽어옵니다.
- **외부 의존성 없음**: 데스크톱 창과 CLI는 Python 표준 라이브러리(`sqlite3`, `tkinter`)만 사용하며, 사이드 패널 플러그인은 Node.js 내장 `node:sqlite`를 사용합니다. `pip install`이나 `npm install`이 필요하지 않습니다.
- **영어 및 중국어 UI 전환**: 기본 상태에서는 간결한 영문 약어(`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`)를 사용하며, 우클릭 메뉴나 패널 상단 버튼을 통해 언제든 중국어로 전환할 수 있습니다.

---

## <a id="quick-start"></a>빠른 시작

### 1. Antigravity 2.0 사이드 패널 플러그인

`~/.gemini/config/plugins/agy-hud`에 설치하면 라이트/다크 테마에 맞춰 자동 전환되는 사이드 패널에서 TPS 차트와 최근 호출 기록을 확인할 수 있습니다:

```bash
python plugin/install_plugin.py
```

제거하려면:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. 독립형 데스크톱 창 & CLI

기존 Antigravity 플러그인 설정을 건드리지 않고 단독으로 실행됩니다:

- **Windows 바탕 화면에서 바로 실행(콘솔 창 없음)**: `desktop/launch.bat` 또는 `desktop/launch.pyw` 더블클릭
- **Python GUI / CLI**:

```bash
# 데스크톱 플로팅 창 실행 (기본: 영어 표시, 500ms 간격 갱신)
python -m desktop.cli

# 터미널에 현재 상태를 한 번만 출력
python -m desktop.cli --cli

# 터미널에서 계속 갱신하며 보기
python -m desktop.cli --watch
```

> [!TIP]
> 플로팅 창의 아무 곳이나 **마우스 오른쪽 버튼으로 클릭**하면 **언어(`EN` / `中文`)**, **항상 위**, **위치 고정**, **투명도(`100%`–`50%`)**, **갱신 주기(`0.5s`–`5s`)**를 변경할 수 있습니다.

---

## <a id="protobuf-map"></a>데이터 필드

AGY-HUD는 `~/.gemini/antigravity/conversations/<uuid>.db`에서 다음 생성 데이터를 읽어옵니다:

| 필드 경로 | 항목 | 대체 경로 |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | 감지된 모델 식별자 (`gemini-3.8-flash-k`) | 표시 이름 (`f1.f21`) |
| `gen_metadata.f1.f4` | 캐시(`f5`), 새 입력(`f2`), 출력(`f3`), 사고(`f9`), 본문 출력(`f10`) | 이전 형식 카운트 (`f1.f17.f2`) |
| `gen_metadata.f1.f9.f10` | 현재 컨텍스트 크기 (`f1`) 및 윈도우 한도 (`f4`, 예: `256,000`) | 모델별 한도 테이블 |
| `gen_metadata.f1.f11` / `f12` | 첫 토큰 지연(`TTFT`) 및 스트리밍 생성 시간 | `0.0s` |
| `steps` (진행 중인 최신 행) | 실행 중인 생성 단계(`step_type = 15`) 경과 시간 | 유휴 상태 |

---

## 프로젝트 구조

```text
agy-hud/
├── desktop/                     # Python 표준 라이브러리 기반 데스크톱 창 & CLI
│   ├── telemetry.py             # 읽기 전용 SQLite + WAL 및 protobuf 파서
│   ├── hud_pill.py              # Tkinter 플로팅 창 및 상세 카드 UI
│   ├── cli.py                   # GUI / --cli / --watch 실행 진입점
│   ├── launch.pyw               # Windows 백그라운드 GUI 실행 스크립트
│   └── launch.bat               # Windows 더블클릭 실행 배치 파일
├── plugin/                      # Antigravity 2.0 사이드 패널 플러그인
│   ├── plugin.json              # 플러그인 매니페스트
│   ├── install_plugin.py        # 설치 / 제거 스크립트
│   ├── assets/logo.svg          # 플러그인 아이콘
│   └── sidecars/hud_panel/      # node:sqlite 백엔드 및 웹뷰 UI
├── docs/
│   └── assets/                  # 배너 및 미리보기용 SVG 이미지
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## 라이선스

[MIT License](LICENSE)를 따릅니다.
