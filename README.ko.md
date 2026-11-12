<div align="center">

<img src="docs/assets/banner.svg" alt="AGY-HUD 배너" width="100%" />

<p>
  <strong>Google Antigravity용 실시간 Token/s, TTFT, 원본 모델 ID 및 컨텍스트 윈도우 HUD</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22c55e?style=flat-square" alt="라이선스: MIT" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B%20Stdlib-3b82f6?style=flat-square" alt="Python 3.9+ 표준 라이브러리" />
  <img src="https://img.shields.io/badge/Node.js-Built--in%20SQLite-06b6d4?style=flat-square" alt="Node.js 내장 SQLite" />
  <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=flat-square" alt="의존성 제로" />
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
  <a href="#protobuf-map">Protobuf 매핑</a> ·
  <a href="CHANGELOG.md">변경 이력</a>
</p>

</div>

---

<div align="center">
  <img src="docs/assets/hud-showcase.svg" alt="AGY-HUD 데스크톱 플로팅 필 및 네이티브 사이드 패널 미리보기" width="100%" />
</div>

---

## <a id="overview"></a>왜 AGY-HUD인가요?

대부분의 토큰 카운터는 API 트래픽을 프록시하거나 클라이언트 측 토크나이저로 크기를 추정합니다. **AGY-HUD**는 Google Antigravity의 로컬 SQLite + WAL 대화 데이터베이스를 엄격한 읽기 전용 모드(`?mode=ro`)로 직접 읽고, 디스크에 저장된 와이어 포맷 protobuf `gen_metadata` 및 `steps` 레코드를 디코딩합니다.

| 핵심 기능 | 상세 설명 |
| :--- | :--- |
| **이중 TPS 지표** | 순수 스트리밍 처리량(`GEN TPS = output / stream_sec`)과 TTFT가 포함된 체감 종단간 속도(`E2E TPS = output / (ttft + stream_sec)`)를 동시에 측정합니다. |
| **버퍼 버스트 가드** | 밀리초 단위의 단일 패킷 도구 플러시(`BUF < 500ms`)를 자동으로 감지해 표시함으로써 `100,000+ tok/s` 같은 가짜 스파이크가 `PEAK TPS`나 차트를 왜곡하지 않도록 보호합니다. |
| **원본 모델 ID 우선순위** | protobuf `f19` 필드(예: `GEMINI-3.8-FLASH-K`)와 실제 컨텍스트 윈도우 한도 `f9.f10.f4`(예: `256,000`)를 직접 우선 읽어옵니다. |
| **외부 의존성 제로** | 데스크톱 플로팅 필과 CLI는 Python 표준 라이브러리(`sqlite3`, `tkinter`)만 사용하며, 사이드 패널 플러그인은 Node.js 내장 `node:sqlite`를 사용합니다. |
| **실시간 EN / 中文 UI 전환** | 기본적으로 간결한 영문 기술 약어(`GEN`, `E2E`, `STR`, `BUF`, `TTFT`, `THK`, `OUT`, `CTX`)를 표시하며, `EN / 中文` 즉시 전환을 지원합니다. |

---

## <a id="quick-start"></a>빠른 시작

### 1. Antigravity 2.0 네이티브 사이드 패널 플러그인

`~/.gemini/config/plugins/agy-hud`에 설치되어 라이트/다크 테마 자동 동기화, TPS 막대 차트, 호출 로그를 제공하는 보조 사이드 패널 뷰로 동작합니다:

```bash
python plugin/install_plugin.py
```

제거하려면:

```bash
python plugin/install_plugin.py --uninstall
```

### 2. 독립형 데스크톱 플로팅 필 & CLI

Antigravity 플러그인을 수정하지 않고 완전히 독립적으로 실행됩니다:

- **Windows GUI (콘솔 창 없음)**: `desktop/launch.bat` 또는 `desktop/launch.pyw` 더블클릭
- **Python GUI / CLI**:

```bash
# 플로팅 HUD 필 실행 (기본값: EN, 500ms 갱신)
python -m desktop.cli

# 터미널 단발성 스냅샷 출력
python -m desktop.cli --cli

# 터미널 실시간 스트리밍 모니터링
python -m desktop.cli --watch
```

> [!TIP]
> 플로팅 필의 아무 곳이나 **마우스 오른쪽 버튼으로 클릭**하면 **언어(`EN` / `中文`)**, **항상 위(Always on Top)**, **위치 고정**, **투명도(`100%`–`50%`)**, **갱신 주기(`0.5s`–`5s`)**를 바꿀 수 있습니다.

---

## <a id="protobuf-map"></a>Protobuf 텔레메트리 맵

AGY-HUD는 `~/.gemini/antigravity/conversations/<uuid>.db`에서 실제 생성 필드를 추출합니다:

| 필드 경로 | 추출 지표 | 폴백(대체 경로) |
| :--- | :--- | :--- |
| `gen_metadata.f1.f19` | 감지된 원본 모델 식별자 (`gemini-3.8-flash-k`) | `f1.f21` 표시 이름 |
| `gen_metadata.f1.f4` | `f5` 캐시, `f2` 새 입력, `f3` 출력, `f9` 사고, `f10` 가시 출력 | `f1.f17.f2` 레거시 사용량 |
| `gen_metadata.f1.f9.f10` | `f1` 활성 컨텍스트 크기, `f4` 윈도우 한도 (`256,000`) | 모델별 한도 조회 테이블 |
| `gen_metadata.f1.f11` / `f12` | `TTFT` 및 스트리밍 생성 `Duration` | `0.0s` |
| `steps` (최신 비종료 단계) | 활성 플래너 단계(`step_type = 15`) 실시간 경과 시간 | 유휴 상태 |

---

## 저장소 구조

```text
agy-hud/
├── desktop/                     # 의존성 없는 Python 데스크톱 필 & CLI
│   ├── telemetry.py             # 읽기 전용 SQLite+WAL 및 protobuf 디코더
│   ├── hud_pill.py              # 프레임리스 Tkinter 필 및 EN/中文 카드 UI
│   ├── cli.py                   # GUI / --cli / --watch 진입점
│   ├── launch.pyw               # Windows 무콘솔 백그라운드 GUI 런처
│   └── launch.bat               # Windows 더블클릭 실행 배치 파일
├── plugin/                      # 네이티브 Antigravity 2.0 사이드 패널 UI 플러그인
│   ├── plugin.json              # Antigravity 플러그인 매니페스트
│   ├── install_plugin.py        # 원커맨드 설치 / 제거 스크립트
│   ├── assets/logo.svg          # 벡터 다이얼 엠블럼
│   └── sidecars/hud_panel/      # node:sqlite 백엔드 및 Webview 대시보드
├── docs/
│   └── assets/                  # SVG 배너 및 UI 미리보기 그래픽
├── pyproject.toml
├── CHANGELOG.md
└── LICENSE
```

---

## 라이선스

[MIT License](LICENSE)에 따라 배포됩니다.
