import os
import json
import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image, ImageOps, ImageEnhance

# Base path of the project
BASE_DIR = Path(__file__).resolve().parent.parent  # /app
print(f"[ImageScraper] BASE_DIR: {BASE_DIR}")

# Paths
CACHE_DIR = BASE_DIR / "image_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
print(f"[ImageScraper] CACHE_DIR: {CACHE_DIR}")

CONFIG_FILE = BASE_DIR / "current_config" / "slides_config.json"
print(f"[ImageScraper] Loading config from: {CONFIG_FILE}")

# Default resolution
DEFAULT_RESOLUTION = (800, 600)

def load_config():
    """Load JSON config, returning dict"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"[ImageScraper] Error loading config: {e}")
    return {}

def parse_resolution(res_str):
    """Parse resolution string like '800x600'"""
    try:
        w, h = map(int, res_str.split('x'))
        return w, h
    except Exception as e:
        print(f"[ImageScraper] Failed to parse resolution '{res_str}', using default: {DEFAULT_RESOLUTION}. Error: {e}")
        return DEFAULT_RESOLUTION

async def screenshot_url(page, url, path, width, height):
    """Take a screenshot using the provided page"""
    try:
        await page.set_viewport_size({"width": width, "height": height})
        await page.goto(url)
        # Take screenshot
        await page.screenshot(path=str(path))
        return True
    except Exception as e:
        print(f"[ImageScraper] Error taking screenshot for {url}: {e}")
        return False

def apply_invert(img, invert=False):
    """Apply invert if requested"""
    if invert:
        print("[ImageScraper] Applying invert")
        return ImageOps.invert(img.convert('RGB'))
    print("[ImageScraper] No invert applied")
    return img

async def save_slide_image(page, slide, config):
    """
    Takes a screenshot of the slide, applies optional grayscale, B/W, contrast, and saves it to image_cache.
    Returns True if saved successfully, False otherwise.
    """
    url = slide.get('url', '').strip()
    if not url:
        print(f"[ImageScraper] Slide '{slide.get('name', 'unknown')}' has no URL, skipping.")
        return False

    timestamp = int(time.time())
    slide_name = slide.get('name', f"slide_{timestamp}")
    output_file = CACHE_DIR / f"{slide_name}_{timestamp}.png"
    print(f"[ImageScraper] Saving slide '{slide_name}': {url}")
    print(f"[ImageScraper] Output file path: {output_file}")

    # Resolution
    res_str = config.get('resolution', '800x600')
    width, height = parse_resolution(res_str)

    # Screenshot
    success = await screenshot_url(page, url, output_file, width, height)
    if not success:
        print(f"[ImageScraper] Screenshot failed for slide '{slide_name}'")
        return False

    # Open image
    try:
        img = Image.open(output_file)
        print(f"[ImageScraper] Opened screenshot image: {output_file.name}")
    except Exception as e:
        print(f"[ImageScraper] Failed to open screenshot image: {e}")
        return False

    # Apply invert
    invert = slide.get('invert', False) or config.get('global', {}).get('invert', False)
    img = apply_invert(img, invert)

    # Convert grayscale if requested
    if config.get('global', {}).get('grayscale', False):
        print("[ImageScraper] Converting to grayscale")
        img = img.convert('L')

    # Boost contrast if requested
    if config.get('global', {}).get('boostContrast', False):
        print("[ImageScraper] Boosting contrast")
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)

    # Convert to B/W if requested
    if config.get('global', {}).get('convertbw', False):
        print("[ImageScraper] Converting to B/W")
        img = img.convert('1')

    # Save final image
    try:
        img.save(output_file)
        print(f"[ImageScraper] Saved slide '{slide_name}' screenshot: {output_file.name}")
        return True
    except Exception as e:
        print(f"[ImageScraper] Failed to save image: {e}")
        return False

async def slide_worker(slide_idx, page, config_getter):
    """Worker task for a single slide, runs independently with its interval"""
    while True:
        config = config_getter()
        slides = config.get('slides', [])
        if slide_idx >= len(slides):
            print(f"[ImageScraper] Slide index {slide_idx} no longer exists in config, sleeping 1 min")
            await asyncio.sleep(60)
            continue

        slide = slides[slide_idx]

        # Check if slide is enabled
        if not slide.get('enabled', True):
            print(f"[ImageScraper] Slide '{slide.get('name', 'unknown')}' is disabled, skipping for now")
            await asyncio.sleep(60)
            continue

        interval = slide.get('interval', config.get('global', {}).get('defaultInterval', 5))
        max_retries = config.get('global', {}).get('maxRetries', 3)

        # Retry loop
        retries = 0
        while retries <= max_retries:
            success = await save_slide_image(page, slide, config)
            if success:
                break
            retries += 1
            print(f"[ImageScraper] Retry {retries}/{max_retries} for slide '{slide.get('name', 'unknown')}'")

        print(f"[ImageScraper] Slide '{slide.get('name', 'unknown')}' done, sleeping for {interval} minutes")
        await asyncio.sleep(interval * 60)

async def run():
    """Main entry point"""
    # Shared browser instance
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width': 800, 'height': 600})
        print("[ImageScraper] Browser launched, starting slide workers")

        # Closure to reload config dynamically
        config_cache = {}
        def get_config():
            nonlocal config_cache
            new_config = load_config()
            if new_config:
                config_cache = new_config
            return config_cache

        # Start workers for up to 4 slides (or however many in config)
        tasks = []
        for i in range(4):
            tasks.append(asyncio.create_task(slide_worker(i, page, get_config)))

        # Wait for all tasks
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run())
