import os
import json
import time
import asyncio
from flask import Flask, send_file
from PIL import Image, ImageOps
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
import datetime

app = Flask(__name__)

CONFIG_FILE = Path('current_config/slides_config.json')
TMP_DIR = Path('/current_image/currentimage')
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Cache last screenshot times per slide
last_screenshot = {}

# Cache current slide images
slide_files = {}

def load_config():
    if CONFIG_FILE.exists():
        return json.load(open(CONFIG_FILE, 'r'))
    return None

def parse_resolution(res_str):
    try:
        w, h = map(int, res_str.split('x'))
        return w, h
    except:
        return 800, 600

def apply_invert(img, invert=False):
    if invert:
        return ImageOps.invert(img.convert('RGB'))
    return img

async def screenshot_url(url, path, width, height):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width': width, 'height': height})
        await page.goto(url)
        await page.screenshot(path=path)
        await browser.close()

def update_slide_image(slide, idx, resolution=None, config=None):
    """
    Check if slide needs a new screenshot, generate it, apply invert and overlay.
    slide: dict from JSON
    idx: slide index
    resolution: optional resolution string like '800x600'
    config: full config dict to pull global and overlay settings
    """
    now = time.time()
    slide_id = f'slide_{idx}'
    last_time = last_screenshot.get(slide_id, 0)
    interval = slide.get('interval', 60)  # screenshot interval

    # Determine resolution
    res_str = resolution or config.get('global', {}).get('resolution', '800x600') if config else '800x600'
    width, height = parse_resolution(res_str)

    output_file = TMP_DIR / f'{slide_id}.png'

    if now - last_time > interval or not output_file.exists():
        # Screenshot URL
        asyncio.run(screenshot_url(slide['url'], output_file, width, height))

        # Open image
        img = Image.open(output_file)

        # Apply per-slide invert
        img = apply_invert(img, slide.get('invert', False))

        # Apply overlay if config provided
        if config:
            overlay_settings = {
                'showTime': slide.get('showTime', False),
                'showDate': slide.get('showDate', False),
                'position': slide.get('position', 'none'),
                'globalInvert': config.get('global', {}).get('invert', False),
                'fontSize': config.get('overlay', {}).get('fontSize', 'medium'),
                'align': config.get('overlay', {}).get('align', 'center')
            }
            img = add_overlay(img, overlay_settings)

        # Save final image
        img.save(output_file)

        # Update caches
        last_screenshot[slide_id] = now
        slide_files[slide_id] = output_file

    return output_file


def add_overlay(img, overlay_settings):
    """
    Adds a date/time overlay box to the image based on overlay_settings.
    overlay_settings dict should contain:
      - showTime (bool)
      - showDate (bool)
      - position ('none', 'top', 'bottom')
      - globalInvert (bool)
      - fontSize ('small', 'medium', 'large')
      - align ('left', 'center', 'right')
    """
    if overlay_settings.get('position') == 'none':
        return img

    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Determine font size as % of image width
    font_pct = {'small': 0.05, 'medium': 0.07, 'large': 0.09}  # 5%, 7%, 9%
    font_size = max(8, int(width * font_pct.get(overlay_settings.get('fontSize', 'medium'), 0.07)))

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Build text
    texts = []
    now = datetime.datetime.now()
    if overlay_settings.get('showTime', False):
        texts.append(now.strftime("%H:%M"))
    if overlay_settings.get('showDate', False):
        texts.append(now.strftime("%-m/%-d/%y"))
    overlay_text = ' '.join(texts)

    if not overlay_text:
        return img

    # Measure text size
    text_width, text_height = draw.textsize(overlay_text, font=font)

    # Determine box position
    box_padding = 5
    box_height = text_height + 2 * box_padding
    if overlay_settings['position'] == 'top':
        y0 = 0
    elif overlay_settings['position'] == 'bottom':
        y0 = height - box_height
    else:
        return img  # safety

    y1 = y0 + box_height
    x0 = 0
    x1 = width

    # Box color
    box_color = (0,0,0) if overlay_settings.get('globalInvert', False) else (255,255,255)
    text_color = (255,255,255) if overlay_settings.get('globalInvert', False) else (0,0,0)

    # Draw rectangle
    draw.rectangle([x0, y0, x1, y1], fill=box_color)

    # Determine text x position based on alignment
    margin = 5
    if overlay_settings.get('align') == 'left':
        text_x = margin
    elif overlay_settings.get('align') == 'right':
        text_x = width - text_width - margin
    else:
        text_x = (width - text_width) // 2

    text_y = y0 + box_padding

    # Draw text
    draw.text((text_x, text_y), overlay_text, font=font, fill=text_color)

    return img

def get_current_slide_idx(num_slides, frequency):
    now = int(time.time())
    return (now // frequency) % num_slides

@app.route('/')
def serve_slide():
    config = load_config()
    if not config:
        return "No config found", 500

    slides = config.get('slides', [])
    if not slides:
        return "No slides configured", 500

    resolution = config.get('global', {}).get('resolution', '800x600')
    slide_frequency = config.get('global', {}).get('slideFrequency', 60)

    idx = get_current_slide_idx(len(slides), slide_frequency)
    slide = slides[idx]

    img_file = update_slide_image(slide, idx, resolution)
    return send_file(img_file, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
