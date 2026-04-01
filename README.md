# Python Project Base

OKX / Binance 자동매매 봇 개발을 위한 프로젝트 템플릿.

---

## 환경

| 항목 | 내용 |
|------|------|
| Python | 3.12.12 (pyenv) |
| 패키지 관리 | Poetry |
| 가상환경 | `.venv` (로컬) |

---

## 새 프로젝트 시작하기

### 1. 템플릿 복사

```bash
cp -r /Users/jypark/moredo/dev/etc/python_project_base /path/to/new_project
cd /path/to/new_project
```

### 2. 가상환경 생성 및 패키지 설치

```bash
rm -rf .venv      # 기존 venv 제거 (절대경로 하드코딩 되어 있어서 재생성 필요)
poetry install
```

### 3. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 API 키 입력:

```
# OKX
OKX_API_KEY=
OKX_SECRET_KEY=
OKX_PASSPHRASE=

# Binance
BINANCE_API_KEY=
BINANCE_SECRET_KEY=

# Telegram
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

---

## 프로젝트 구조

```
project/
├── config/
│   ├── settings.py     # API 키, SYMBOLS, WS URL (OKX / Binance / Telegram)
│   └── logger.py       # loguru 로깅 설정
├── db/
│   └── candle_store.py # SQLite 캔들 저장 (init_db, upsert_candle, get_last_ts, backfill_recent)
├── notify/
│   └── telegram.py     # 텔레그램 메시지 / 파일 전송
├── data/               # DB 파일 저장 (gitignore)
├── logs/               # 로그 파일 저장 (gitignore)
├── .env.example        # 환경변수 템플릿
├── .gitignore
├── Makefile
├── pyproject.toml
└── poetry.lock
```

새 프로젝트에서 필요한 모듈(collector, strategy, trader, order 등)을 추가해서 사용.

---

## 주요 패키지

| 패키지 | 용도 |
|--------|------|
| websockets | WebSocket 연결 (거래소 실시간 데이터) |
| aiohttp | REST API 호출 |
| pandas | 데이터 처리 / 지표 계산 |
| numpy | 수치 계산 |
| loguru | 로깅 |
| python-dotenv | `.env` 환경변수 로드 |
| openpyxl / lxml | 엑셀 출력 (백테스트 결과 등) |

---

## 사용법

### 로깅

진입점 파일(`main.py` 등) 최상단에 한 번만 호출:

```python
from config.logger import setup_logger
setup_logger()  # logs/app.log 에 저장, 10MB 로테이션, 30일 보관
```

이후 어디서든:

```python
from loguru import logger

logger.info("봇 시작")
logger.warning("주의 메시지")
logger.error("에러 발생")
```

로그 파일 경로 변경:

```python
setup_logger(log_file="logs/trader.log", level="DEBUG")
```

### 텔레그램 알림

```python
import asyncio
from notify.telegram import send, send_file

# 메시지 전송
await send("롱 진입: BTC-USDT-SWAP @ 90,000")

# 파일 전송
with open("result.xlsx", "rb") as f:
    await send_file(f.read(), "result.xlsx", caption="백테스트 결과")
```

`.env`에 `TELEGRAM_TOKEN`과 `TELEGRAM_CHAT_ID`가 없으면 자동으로 스킵.

### 설정값 참조

```python
from config.settings import OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE
from config.settings import OKX_WS_PUBLIC, OKX_WS_BUSINESS, OKX_WS_PRIVATE, OKX_REST_URL
from config.settings import BINANCE_API_KEY, BINANCE_SECRET_KEY
from config.settings import BINANCE_WS_PUBLIC, BINANCE_REST_URL
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from config.settings import SYMBOLS
```

심볼 목록은 `config/settings.py`의 `SYMBOLS` 리스트에서 관리:

```python
SYMBOLS = [
    "BTC-USDT-SWAP",
    "ETH-USDT-SWAP",   # 주석 해제하면 추가됨
]
```

### DB (캔들 저장)

```python
from db.candle_store import init_db, upsert_candle, get_last_ts, backfill_recent

# 초기화 (최초 1회)
init_db()

# 최근 캔들 백필 (데이터 없을 때 자동 수집)
await backfill_recent("BTC-USDT-SWAP", count=1100)

# 캔들 저장 (WebSocket 수신 시)
upsert_candle(symbol="BTC-USDT-SWAP", ts=ts, open_=o, high=h, low=l, close=c, volume=v, confirm=1)

# 마지막 저장 ts 조회 (gap fill 용)
last_ts = get_last_ts("BTC-USDT-SWAP")
```

### Makefile

```bash
make run    # PYTHONPATH=. poetry run python main.py
```

새 명령어 추가 예시:

```makefile
PYTHON = PYTHONPATH=. poetry run python

collect:
    $(PYTHON) collector/ws_collector.py

trader:
    $(PYTHON) trader/position_manager.py
```

---

## 패키지 추가

```bash
poetry add 패키지명
```

---

## 참고

- 베이스 프로젝트: Pi_okx (OKX 자동매매 봇) 구조 기반
- `.venv`, `.env`, `data/`, `logs/` 는 `.gitignore`에 포함
# okx2
