import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


def log_elapsed(
    start_time: float,
    category: str,
    task: str,
    tags: Optional[list[str]] = None,
    level: int = logging.INFO,
):
    elapsed = time.perf_counter() - start_time
    tag_str = " ".join(f"[{tag}]" for tag in tags) if tags else ""

    message = f"[{category}] {task} - Elapsed: {elapsed:.3f}s {tag_str}".strip()
    logger.log(level, message)
