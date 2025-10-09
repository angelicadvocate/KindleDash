import os
import json
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import datetime

# Base path of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
CACHE_DIR = BASE_DIR / "image_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = BASE_DIR / "current_config" / "slides_config.json"

# ---------------------------
# Helper to load config
# ---------------------------
def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

# ---------------------------
# Overlay function
# ---------------------------
def add_overlay(img_path, config):
    overlay_cfg = config.get('overlay', {})
    global_cfg = config.get('global', {})

    img = Image.open(img_path)

    # Apply global inversion if configured
    if global_cfg.get('invert', False):
        img = ImageOps.invert(img.convert('RGB'))

    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Build overlay text
    texts = []
    now = datetime.datetime.utcnow()  # default UTC
    tz = global_cfg.get('timezone', 'UTC')  # placeholder for future timezone logic
    if overlay_cfg.get('showTime', False):
        texts.append(now.strftime("%H:%M"))
    if overlay_cfg.get('showDate', False):
        texts.append(now.strftime("%-m/%-d/%y"))
    overlay_text = ' '.join(texts)

    if overlay_text:
        # Font setup
        font_size_map = {'small': 0.05, 'medium': 0.07, 'large': 0.09}
        font_size = max(8, int(width * font_size_map.get(overlay_cfg.get('fontSize', 'medium'), 0.07)))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text_width, text_height = draw.textsize(overlay_text, font=font)
        box_padding = 5
        box_height = text_height + 2 * box_padding

        # Determine position
        pos = overlay_cfg.get('position', 'top')
        if pos == 'top':
            y0 = 0
        elif pos == 'bottom':
            y0 = height - box_height
        else:
            y0 = 0  # default
        y1 = y0 + box_height

        # Colors
        box_color = (0, 0, 0) if global_cfg.get('invert', False) else (255, 255, 255)
        text_color = (255, 255, 255) if global_cfg.get('invert', False) else (0, 0, 0)

        # Draw box and text
        draw.rectangle([0, y0, width, y1], fill=box_color)
        align = overlay_cfg.get('align', 'center')
        if align == 'left':
            x = 5
        elif align == 'right':
            x = width - text_width - 5
        else:
            x = (width - text_width) // 2
        y = y0 + box_padding
        draw.text((x, y), overlay_text, font=font, fill=text_color)

    # Boost contrast if configured
    if global_cfg.get('boostContrast', False):
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)

    # Grayscale/BW if needed
    if global_cfg.get('grayscale', False):
        img = img.convert('L')
    if global_cfg.get('convertbw', False):
        img = img.convert('1')

    # Always save with O_ prefix
    output_path = img_path.parent / f"O_{img_path.name}"
    img.save(output_path)
    print(f"Overlay processed: {output_path.name}")

# ---------------------------
# Main watcher loop
# ---------------------------
def run():
    config = load_config()
    print("Overlay manager started, watching image cache...")

    while True:
        for img_file in CACHE_DIR.iterdir():
            # Only process files not already prefixed with O_
            if img_file.is_file() and not img_file.name.startswith("O_"):
                try:
                    add_overlay(img_file, config)
                except Exception as e:
                    print(f"Failed to process {img_file.name}: {e}")
        time.sleep(30)  # check every 30 seconds

if __name__ == "__main__":
    run()
