import logging
import aiohttp

from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

BASE_URL     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
DOCUMENT_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


async def send(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(BASE_URL, json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": _escape_html(text),
                "parse_mode": "HTML",
            }) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.error(f"[텔레그램] 전송 실패: status={resp.status} body={body}")
    except Exception as e:
        logger.error(f"[텔레그램] 전송 실패: {e}")


async def send_file(file_bytes: bytes, filename: str, caption: str = ""):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("chat_id", str(TELEGRAM_CHAT_ID))
            form.add_field("document", file_bytes, filename=filename, content_type="application/octet-stream")
            if caption:
                form.add_field("caption", caption)
            await session.post(DOCUMENT_URL, data=form)
    except Exception as e:
        logger.error(f"[텔레그램] 파일 전송 실패: {e}")
