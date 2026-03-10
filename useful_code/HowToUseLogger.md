# ロガーの使い方
# main.py
from mini_logger import get_logger

logger = get_logger(__name__, level="DEBUG", log_file="logs/app.log", rotate_by="size")
logger.info("起動します")
try:
    1 / 0
except Exception:
    logger.exception("何か例外が発生しました")
