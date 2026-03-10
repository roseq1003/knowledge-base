# mini_logger.py
import logging
import logging.handlers
import os
from typing import Optional

_DEFAULT_FMT = "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
_DEBUG_FMT = "[%(asctime)s] %(levelname)s %(name)s:%(funcName)s:%(lineno)d - %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: Optional[str] = None,
    level: str = "INFO",
    log_file: Optional[str] = None,
    rotate_by: str = "size",       # "size" or "time"
    max_bytes: int = 1_000_000,    # rotate_by="size"のとき
    backup_count: int = 5,
    when: str = "midnight",        # rotate_by="time"のとき
    utc: bool = False,
    debug_format: bool = False,
    propagate: bool = False,
) -> logging.Logger:
    """
    どこでも使える汎用ロガー。
    - コンソール & 任意でファイル出力（ローテーション対応）
    - 関数名/行番号の詳細表示（debug_format=True）
    - 依存なし（標準ライブラリのみ）

    使い方:
        from mini_logger import get_logger
        logger = get_logger(__name__, level="DEBUG", log_file="app.log")
        logger.info("Hello")

    主な引数:
        level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL"
        log_file: パスを渡すとファイル出力を有効化
        rotate_by: "size"（サイズ）か "time"（日次など）
    """
    logger = logging.getLogger(name if name else "app")

    # すでにハンドラが付いていたら二重付与を避ける
    if logger.handlers:
        return logger

    # レベル設定
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # フォーマット
    fmt = _DEBUG_FMT if debug_format or numeric_level <= logging.DEBUG else _DEFAULT_FMT
    formatter = logging.Formatter(fmt=fmt, datefmt=_DATEFMT)

    # コンソール
    sh = logging.StreamHandler()
    sh.setLevel(numeric_level)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # ファイル（任意）
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        if rotate_by == "time":
            fh = logging.handlers.TimedRotatingFileHandler(
                log_file, when=when, interval=1, backupCount=backup_count, utc=utc, encoding="utf-8"
            )
        else:
            fh = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )
        fh.setLevel(numeric_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # ルートに伝播させない（重複出力防止）
    logger.propagate = propagate

    # よく騒ぐ外部ライブラリのログを下げたい場合はここで調整
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger
