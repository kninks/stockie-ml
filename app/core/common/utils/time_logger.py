import logging
import time

logger = logging.getLogger(__name__)


def log_start(task: str):
    logger.info(f"[Start] {task}")
    return time.perf_counter(), task


def log_end(start_time: float, task: str):
    elapsed = time.perf_counter() - start_time
    logger.info(f"[End] {task} | Elapsed: {elapsed:.3f}s")
