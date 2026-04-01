import sys
from loguru import logger


def setup_logger(log_file: str = "logs/app.log", level: str = "INFO"):
    logger.remove()

    # 콘솔 출력
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # 파일 저장 (10MB마다 로테이션, 30일 보관)
    logger.add(
        log_file,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name} - {message}",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
    )
