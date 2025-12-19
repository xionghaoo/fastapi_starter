import os
import sys
from datetime import datetime
from pathlib import Path
from loguru import logger
from app.core.config import settings


def configure_logging() -> None:
    log_dir = Path(os.getenv("LOG_DIR", settings.log_dir))
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    level = settings.log_level.upper()
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(sys.stderr, level=level, format=fmt, enqueue=True, backtrace=False, diagnose=False)

    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    logger.add(log_dir / f"app-info-{date_str}.log", level="INFO", rotation="10 MB", retention="14 days", format=fmt, enqueue=True)
    logger.add(log_dir / f"app-error-{date_str}.log", level="ERROR", rotation="10 MB", retention="30 days", format=fmt, enqueue=True)


