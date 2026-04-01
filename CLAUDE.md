# CLAUDE.md

이 파일을 읽으면 아래 순서대로 환경을 확인하고 셋팅해줘.

---

## 프로젝트 개요

OKX / Binance 자동매매 봇 개발용 베이스 템플릿에서 클론한 프로젝트.
`python_project_base`를 복사해서 시작했기 때문에 아래 구조와 파일들이 기본으로 포함되어 있음.

---

## 세션 시작 시 환경 확인 순서

### 1. .venv 확인
```bash
ls .venv
```
없으면 자동으로 생성:
```bash
poetry install
```

### 2. .env 확인
```bash
ls .env
```
없으면 안내:
```
.env 파일이 없습니다. cp .env.example .env 후 API 키를 입력해주세요.
```

### 3. Python 버전 확인
`.python-version` 파일 기준 3.12.12 (pyenv).
`python` 명령이 안 되면 pyenv PATH 초기화 필요:
```bash
export PATH="$HOME/.pyenv/bin:$HOME/.pyenv/shims:$PATH" && eval "$(pyenv init -)"
```

---

## 프로젝트 구조

```
project/
├── config/
│   ├── settings.py     # API 키, SYMBOLS, WS URL 로드
│   └── logger.py       # loguru 로깅 초기화
├── db/
│   └── candle_store.py # SQLite 캔들 저장 (init_db, upsert_candle, get_last_ts, backfill_recent)
├── notify/
│   └── telegram.py     # 텔레그램 메시지 / 파일 전송
├── data/               # DB 파일 저장 (gitignore)
├── logs/               # 로그 파일 저장 (gitignore)
├── .env.example        # 환경변수 템플릿
├── Makefile
└── README.md
```

프로젝트별로 추가하는 모듈: `collector/`, `strategy/`, `trader/`, `order/`

---

## 핵심 파일 역할

### config/settings.py
- `.env`에서 API 키 로드
- `SYMBOLS` 리스트로 구독 심볼 관리
- OKX / Binance WS URL 및 REST URL 상수 정의

### config/logger.py
- `setup_logger()` — 진입점 파일 최상단에서 한 번 호출
- 콘솔 + 파일(`logs/app.log`) 동시 출력
- 10MB 로테이션, 30일 보관

### db/candle_store.py
- `init_db()` — SQLite 테이블 생성 (최초 1회)
- `upsert_candle()` — WebSocket 수신 캔들 저장
- `get_last_ts()` — 마지막 확정 캔들 ts 조회 (gap fill 용)
- `backfill_recent()` — OKX REST로 초기 데이터 수집

### notify/telegram.py
- `send(text)` — 텔레그램 메시지 전송
- `send_file(bytes, filename)` — 파일 전송
- `.env`에 토큰/chat_id 없으면 자동 스킵

---

## 개발 패턴

- 비동기 기반: `asyncio` + `aiohttp` + `websockets`
- 실행: `PYTHONPATH=. poetry run python` (Makefile의 `PYTHON` 변수)
- 로깅: `logging` 대신 `loguru` 사용
- DB: SQLite (`data/candles.db`), WAL 모드
- 환경변수: `python-dotenv`로 `.env` 로드

### WebSocket 핵심 패턴 (Pi_okx 기반)
- 25초마다 ping 전송으로 연결 유지
- 재연결 시 gap fill (REST로 누락 캔들 채움)
- 5분 경계 감지: `(ts + 60_000) % 300_000 == 0`

---

## 패키지

| 패키지 | 용도 |
|--------|------|
| websockets | WebSocket 연결 |
| aiohttp | REST API 호출 |
| pandas | 데이터 처리 / 지표 계산 |
| numpy | 수치 계산 |
| loguru | 로깅 |
| python-dotenv | `.env` 로드 |
| openpyxl / lxml | 엑셀 출력 |

패키지 추가: `poetry add 패키지명`

---

## 참고

- 베이스 템플릿 위치: `/Users/jypark/moredo/dev/etc/python_project_base`
- 참조 프로젝트: Pi_okx (`/Users/jypark/moredo/dev/etc/Pi_okx`) — OKX BTC 자동매매 봇
  - ws_collector.py가 핵심 (WebSocket 수집 + 5분 경계 신호 감지 + 주문)
  - SMMA 크로스오버 전략, 레버리지 10x, TP/SL 1%
