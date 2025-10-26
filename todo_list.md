# KindleDash TODO List

## 🔴 Critical Issues

### Image Cycling Problems
**Location:** `src/move_current_image.py`

**Current Issues:**
1. **Index Reset Bug**: The `current_index` variable properly cycles through slides, but if the enabled slides list changes between iterations (slides added/removed/disabled), the index may become invalid or point to the wrong slide.
2. **No Graceful Handling of Missing Images**: If `get_latest_slide_image()` returns `None` (no image available for a slide), the system silently fails to update without informing the user or skipping to the next slide.
3. **No State Persistence**: When the service restarts, it always starts from index 0. This means the same slide always shows first after restart.
4. **Race Condition**: The image scraper may not have created an image for a newly enabled slide yet, causing the cycling to show stale or missing images.

**Recommended Solutions:**
1. **Validate index on each iteration**: Before using `current_index`, check if it's still valid for the current `enabled_slides` list length. Reset to 0 if out of bounds.
2. **Implement retry logic**: If a slide has no image available, log a warning and try the next slide instead of just skipping the update.
3. **Add state file**: Save the last shown slide index and timestamp to a JSON file (e.g., `current_config/cycling_state.json`) and restore on startup.
4. **Add slide readiness check**: Before cycling to a slide, verify that at least one processed image (with `O_` prefix) exists for it.
5. **Better logging**: Add timestamps and more detailed logging about which slide is being shown and why certain slides are skipped.

**Implementation Considerations:**
```python
# Suggested improvements:
# 1. Validate index bounds and handle empty list
if not enabled_slides:
    print("[MoveImage] No enabled slides, sleeping...")
    time.sleep(60)
    continue
    
if current_index >= len(enabled_slides):
    current_index = 0
    
# 2. Retry logic for missing images
attempts = 0
max_attempts = len(enabled_slides)
while attempts < max_attempts:
    slide_name = enabled_slides[current_index]
    if get_latest_slide_image(slide_name):
        update_current_image(slide_name)
        break
    else:
        print(f"[MoveImage] No image for {slide_name}, trying next slide")
        current_index = (current_index + 1) % len(enabled_slides)
        attempts += 1

# 3. State persistence
STATE_FILE = BASE_DIR / "current_config" / "cycling_state.json"

def save_state(index):
    state = {'current_index': index, 'timestamp': time.time()}
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f).get('current_index', 0)
    return 0
```

---

## 🟡 High Priority Features

### 1. Authentication System
**Status:** Partially implemented (frontend exists but not integrated)
- [ ] Complete backend authentication API endpoints
- [ ] Add user session management
- [ ] Integrate login/register pages with backend
- [ ] Add password hashing and security measures
- [ ] Add authentication middleware to protect configurator routes

**Files to modify:**
- `src/webserve.py` - Add auth endpoints and middleware
- `frontend/auth/` - Already has frontend templates

### 2. Configuration API
**Status:** Missing
- [ ] Add REST API endpoints to read/update `slides_config.json`
- [ ] Add validation for configuration changes
- [ ] Add endpoint to save configuration from the web configurator
- [ ] Add endpoint to reset to default configuration

**Suggested endpoints:**
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration
- `POST /api/config/reset` - Reset to defaults
- `GET /api/slides/{slide_name}/preview` - Get preview of a specific slide

### 3. Real-time Preview
**Status:** Missing
- [ ] Add endpoint to serve the current displayed image
- [ ] Add auto-refresh in configurator to show what Kindle sees
- [ ] Add manual refresh button
- [ ] Show last update timestamp

### 4. Slide Management
**Status:** Basic implementation exists
- [ ] Add ability to reorder slides via drag-and-drop in configurator
- [ ] Add slide preview/thumbnail generation
- [ ] Add ability to test a slide URL before saving
- [ ] Add slide history/version tracking
- [ ] Support for local image uploads (not just URLs)

---

## 🟢 Medium Priority Features

### 5. Error Handling & Monitoring
**Location:** All Python modules
- [ ] Add comprehensive try-catch blocks throughout
- [ ] Implement proper error logging with log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Add health check endpoint (`/health`) for monitoring
- [ ] Add metrics endpoint to show system status
- [ ] Improve logger.py to send alerts/notifications on failures

### 6. Overlay Manager Enhancements
**Location:** `src/overlay_manager.py`
- [ ] Add support for custom text overlays (not just time/date)
- [ ] Add support for multiple overlay positions (corners, center)
- [ ] Add weather overlay integration
- [ ] Add battery level overlay (if Kindle reports it)
- [ ] Fix timezone support (currently hardcoded to UTC)
- [ ] Add configurable date/time formats

### 7. Image Scraper Improvements
**Location:** `src/image_scraper.py`
- [ ] Add support for authentication on scraped sites (username/password)
- [ ] Add support for custom JavaScript execution before screenshot
- [ ] Add wait conditions (wait for specific element to load)
- [ ] Add support for scrolling screenshots (full page capture)
- [ ] Add retry with exponential backoff
- [ ] Add user-agent customization per slide
- [ ] Optimize browser memory usage (currently one page shared by all workers)

### 8. Garbage Collector Enhancements
**Location:** `src/garbage_collector.py`
- [ ] Make cache duration configurable from `slides_config.json`
- [ ] Add cache size limits (delete oldest if cache exceeds X MB)
- [ ] Add selective cleanup (keep at least N images per slide)
- [ ] Add manual cleanup trigger endpoint

---

## 🔵 Low Priority / Nice to Have

### 9. Documentation
- [ ] Complete README.md with full setup instructions
- [ ] Add Docker Hub publishing instructions
- [ ] Add troubleshooting guide
- [ ] Add example configurations for common use cases
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Add contribution guidelines
- [ ] Add architecture diagram

### 10. Docker & Deployment
**Location:** `Dockerfile`, `supervisord.conf`
- [ ] Optimize Docker image size (currently using full Python image)
- [ ] Add docker-compose.yml for easier local development
- [ ] Add environment variable support for configuration
- [ ] Add volume mounts for persistent data
- [ ] Create multi-architecture builds (ARM for Raspberry Pi)
- [ ] Add health checks to supervisord processes

### 11. Testing
**Status:** No tests currently exist
- [ ] Add unit tests for all Python modules
- [ ] Add integration tests for the full workflow
- [ ] Add frontend tests for configurator
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Add code coverage reporting

### 12. Performance Optimizations
- [ ] Add caching headers to web server responses
- [ ] Optimize image compression (balance quality vs file size)
- [ ] Add lazy loading for configurator
- [ ] Profile and optimize Python code
- [ ] Consider async/await for move_current_image.py

### 13. Frontend Configurator Enhancements
**Location:** `frontend/configurator/`
- [ ] Add dark mode support
- [ ] Improve mobile responsiveness
- [ ] Add form validation before saving
- [ ] Add unsaved changes warning
- [ ] Add export/import configuration feature
- [ ] Add slide templates/presets
- [ ] Add color picker for overlay colors
- [ ] Add font selection for overlays

### 14. Advanced Features
- [ ] Multi-device support (manage multiple Kindles)
- [ ] Scheduling (different slides at different times)
- [ ] Weather integration (actual weather widgets, not just weather.com)
- [ ] Calendar integration (Google Calendar, iCal)
- [ ] RSS feed support
- [ ] Custom widget support (extensible plugin system)
- [ ] Slide transitions/animations configuration
- [ ] Remote control (advance/previous slide on demand)

---

## 🛠️ Code Quality & Maintenance

### 15. Code Improvements
- [ ] Add type hints to all Python functions
- [ ] Add docstrings to all functions and modules
- [ ] Standardize logging format across all modules
- [ ] Add configuration validation schema (JSON Schema or Pydantic)
- [ ] Refactor common code into shared utilities module
- [ ] Add pre-commit hooks for code formatting (black, flake8)
- [ ] Add requirements-dev.txt for development dependencies

### 16. Security
- [ ] Implement rate limiting on API endpoints
- [ ] Add CSRF protection for configurator
- [ ] Sanitize user inputs (URLs, overlay text)
- [ ] Add HTTPS support
- [ ] Regular dependency updates for security patches
- [ ] Add secrets management (don't hardcode sensitive data)
- [ ] Implement proper CORS configuration

---

## 📋 Bugs & Issues

### Known Issues
1. **Overlay Manager**: Doesn't reload config dynamically - requires restart to pick up overlay changes
2. **Image Scraper**: Fixed to 4 slide workers - doesn't dynamically adjust to actual number of slides
3. **Timezone**: Overlay uses UTC hardcoded, should use configured timezone
4. **Font Handling**: Falls back to default font if arial.ttf not found - should package fonts or handle better
5. **Config Reload**: Most modules load config only on startup or in loop, changes don't apply immediately
6. **Port Configuration**: Ports hardcoded to 5000 (Flask) - should be configurable via environment variables
7. **Error Messages**: Many generic error messages don't provide enough context for debugging
8. **Move Current Image**: No handling for when enabled_slides list is empty during runtime

---

## 🎯 Quick Wins (Easy fixes for immediate value)

1. **Fix image cycling bug** - Add index validation and retry logic
2. **Add /health endpoint** - Simple endpoint returning "OK" for monitoring
3. **Add basic API for config** - At minimum, GET endpoint to read current config
4. **Improve error messages** - Add more context to print statements
5. **Add .gitignore** - Exclude `image_cache/`, `current_image/`, `__pycache__/`, etc.
6. **Add VERSION endpoint** - Serve the VERSION file content via API
7. **Environment variables** - Support PORT, CACHE_DIR, CONFIG_FILE via env vars
8. **Fix overlay timezone** - Use pytz with configured timezone instead of UTC

---

## Version Roadmap Suggestion

### v0.2.0-alpha (Next Release)
- Fix critical image cycling bugs
- Add basic configuration API
- Add health check endpoint
- Improve error handling and logging

### v0.3.0-alpha
- Complete authentication system
- Add real-time preview
- Improve slide management UI
- Add basic tests

### v0.4.0-beta
- Advanced overlay features
- Slide scheduling
- Multi-device support
- Comprehensive documentation

### v1.0.0 (Production Ready)
- All critical features implemented
- Full test coverage
- Security audit completed
- Production-ready documentation
