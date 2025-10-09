import os
import time
import json
from pathlib import Path
import shutil

# Base path of the project
BASE_DIR = Path(__file__).resolve().parent.parent  # /app

# Paths
CACHE_DIR = BASE_DIR / "image_cache"
CURRENT_DIR = BASE_DIR / "current_image"
CURRENT_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = BASE_DIR / "current_config" / "slides_config.json"

# Default update interval in seconds if JSON is missing
UPDATE_INTERVAL = 60

def load_config():
    """Load JSON config"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[MoveImage] Error loading config: {e}")
    return {}

def get_slide_frequency(config):
    """Return slide rotation frequency from JSON global section (in seconds)"""
    return config.get('global', {}).get('slideFrequency', 60)

def get_enabled_slides(config):
    """Return list of enabled slide names in order"""
    return [s['name'] for s in config.get('slides', []) if s.get('enabled', True)]

def get_latest_slide_image(slide_name):
    """
    Returns the most recent cached image for a given slide name.
    Only considers images starting with 'O_' to ensure they have been processed by overlay manager.
    """
    images = sorted(
        [f for f in CACHE_DIR.iterdir() 
         if f.is_file() and f.name.startswith(f"O_{slide_name}_")],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    return images[0] if images else None

def update_current_image(slide_name):
    """
    Moves the latest cached slide image to the current_image directory.
    """
    img_file = get_latest_slide_image(slide_name)
    if img_file:
        dest_file = CURRENT_DIR / 'currentimage.png'
        try:
            shutil.copy(img_file, dest_file)
            print(f"[MoveImage] Updated current image with: {img_file.name}")
        except Exception as e:
            print(f"[MoveImage] Error updating current image: {e}")

def run():
    """
    Continuously update the current image based on enabled slides rotation.
    """
    current_index = 0  # track which slide to show next

    while True:
        config = load_config()
        slide_frequency = get_slide_frequency(config)
        enabled_slides = get_enabled_slides(config)

        if not enabled_slides:
            print("[MoveImage] No enabled slides, sleeping 1 minute...")
            time.sleep(60)
            continue

        # Determine the slide to display in order
        slide_name = enabled_slides[current_index]
        update_current_image(slide_name)

        # Move to the next slide for next iteration
        current_index = (current_index + 1) % len(enabled_slides)

        # Sleep for the configured slide frequency
        time.sleep(slide_frequency)

if __name__ == "__main__":
    print("[MoveImage] Starting slide rotation process...")
    run()
