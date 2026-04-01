import sqlite3
from pathlib import Path

import aiohttp
from loguru import logger

from config.settings import OKX_REST_URL

DB_PATH = Path("data/candles.db")
CANDLES_ENDPOINT = "/api/v5/market/candles"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS candles_1m (
                symbol   TEXT    NOT NULL,
                ts       INTEGER NOT NULL,
                open     REAL    NOT NULL,
                high     REAL    NOT NULL,
                low      REAL    NOT NULL,
                close    REAL    NOT NULL,
                volume   REAL    NOT NULL,
                confirm  INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (symbol, ts)
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_candles_1m_symbol_ts ON candles_1m (symbol, ts)"
        )


def upsert_candle(symbol: str, ts: int, open_: float, high: float, low: float,
                  close: float, volume: float, confirm: int):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO candles_1m (symbol, ts, open, high, low, close, volume, confirm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (symbol, ts) DO UPDATE SET
                open    = excluded.open,
                high    = excluded.high,
                low     = excluded.low,
                close   = excluded.close,
                volume  = excluded.volume,
                confirm = excluded.confirm
        """, (symbol, ts, open_, high, low, close, volume, confirm))


def get_last_ts(symbol: str) -> int | None:
    """심볼의 마지막 확정 캔들 ts(ms) 반환. 없으면 None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT MAX(ts) FROM candles_1m WHERE symbol = ? AND confirm = 1",
            (symbol,)
        ).fetchone()
    return row[0] if row and row[0] is not None else None


async def backfill_recent(symbol: str, count: int = 1100):
    """최근 count개 1분봉을 REST API로 수집해 저장. 이미 데이터 있으면 스킵."""
    if get_last_ts(symbol) is not None:
        logger.info(f"[backfill] {symbol} 이미 데이터 있음, 스킵")
        return

    logger.info(f"[backfill] {symbol} 최근 {count}개 1분봉 수집 시작...")
    all_rows = []
    after = None

    async with aiohttp.ClientSession() as session:
        while len(all_rows) < count:
            params = {"instId": symbol, "bar": "1m", "limit": 300}
            if after:
                params["after"] = after

            async with session.get(OKX_REST_URL + CANDLES_ENDPOINT, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()

            if data.get("code") != "0":
                raise RuntimeError(f"OKX API 에러: {data.get('msg')}")

            batch = data.get("data", [])
            if not batch:
                break

            all_rows.extend(batch)
            after = batch[-1][0]

            if len(batch) < 300:
                break

    confirmed = [r for r in all_rows if r[8] == "1"][:count]
    for row in confirmed:
        upsert_candle(
            symbol  = symbol,
            ts      = int(row[0]),
            open_   = float(row[1]),
            high    = float(row[2]),
            low     = float(row[3]),
            close   = float(row[4]),
            volume  = float(row[5]),
            confirm = int(row[8]),
        )

    logger.info(f"[backfill] {symbol} {len(confirmed)}개 저장 완료")
