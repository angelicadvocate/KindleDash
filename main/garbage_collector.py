import os
import sys
import time
import traceback
from pathlib import Path

# --- Configuration ---
CACHE_DIR = Path(__file__).resolve().parent.parent / "image_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MAX_AGE_SECONDS = 30 * 60      # 30 minutes
CHECK_INTERVAL_SECONDS = 5 * 60  # 5 minutes
STARTUP_DELAY_SECONDS = 30     # Delay before starting cleanup

def cleanup_cache():
    """Delete files older than MAX_AGE_SECONDS from CACHE_DIR."""
    now = time.time()
    for file in CACHE_DIR.iterdir():
        if file.is_file():
            file_age = now - file.stat().st_mtime
            if file_age > MAX_AGE_SECONDS:
                try:
                    file.unlink()
                    print(f"[GarbageCollector] Deleted stale cache file: {file.name}")
                except Exception as e:
                    print(f"[GarbageCollector] Error deleting {file.name}: {e}")

def run():
    print(f"[GarbageCollector] Starting in {STARTUP_DELAY_SECONDS} seconds...")
    time.sleep(STARTUP_DELAY_SECONDS)
    print("[GarbageCollector] Monitoring image cache now...")
    while True:
        cleanup_cache()
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run()
