import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

from pathlib import Path

# Base path of the project
BASE_DIR = Path(__file__).resolve().parent.parent  # assumes script is in /app/main

# Directories
CACHE_DIR = BASE_DIR / "image_cache"
CURRENT_DIR = BASE_DIR / "current_image"
CURRENT_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = BASE_DIR / "current_config" / "slides_config.json"

def run():
    print("Logger started...")
    while True:
        # your monitoring logic here
        time.sleep(30)

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_slide_files(directory, prefix_filter=None):
    files = [f for f in directory.iterdir() if f.is_file()]
    if prefix_filter:
        files = [f for f in files if f.name.startswith(prefix_filter)]
    return files

def log_workflow():
    config = load_config()
    slides = config.get('slides', [])
    global_cfg = config.get('global', {})
    slide_frequency = global_cfg.get('slideFrequency', 60)  # in seconds
    default_interval = global_cfg.get('defaultInterval', 5)  # in minutes

    while True:
        now = time.time()
        print(f"\n=== LOGGER CHECK: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} ===")

        # ---- Move Current Image check ----
        current_files = get_slide_files(CURRENT_DIR)
        if current_files:
            latest_current_mtime = max(f.stat().st_mtime for f in current_files)
            delta = now - latest_current_mtime
            if delta > slide_frequency:
                print(f"[WARNING] Move current image may have stalled! Latest file {delta:.0f}s old.")
        else:
            print("[WARNING] No files in current_image directory!")

        # ---- Overlay Manager check ----
        unprocessed_files = get_slide_files(CACHE_DIR, prefix_filter="slide_")
        if unprocessed_files:
            oldest_unprocessed = min(f.stat().st_mtime for f in unprocessed_files)
            if (now - oldest_unprocessed) > 300 and len(unprocessed_files) > 1:  # older than 5 minutes
                print(f"[WARNING] Overlay manager may not be running! {len(unprocessed_files)} unprocessed files.")
        else:
            print("Overlay manager OK: no unprocessed files.")

        # ---- Garbage Collector check ----
        old_cache_files = [f for f in CACHE_DIR.iterdir() if f.is_file() and (now - f.stat().st_mtime) > 3600]  # older than 1 hour
        if old_cache_files:
            print(f"[WARNING] Garbage collector may not have run! {len(old_cache_files)} files older than 1 hour.")

        # ---- Image Scraper check ----
        scraper_interval = default_interval * 60
        latest_cache_mtime = None
        all_cache_files = get_slide_files(CACHE_DIR)
        if all_cache_files:
            latest_cache_mtime = max(f.stat().st_mtime for f in all_cache_files)
            delta = now - latest_cache_mtime
            if delta > scraper_interval:
                print(f"[WARNING] Image scraper may have stalled! Latest cached image {delta:.0f}s old.")
        else:
            print("[WARNING] No images found in cache! Image scraper may not have run.")

        # Sleep before next check
        time.sleep(30)

if __name__ == "__main__":
    log_workflow()
