from __future__ import annotations

import logging
import sys

def setup_logging() -> logging.Logger:
    logger = logging.getLogger("streaming_anomaly_platform")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logging()
