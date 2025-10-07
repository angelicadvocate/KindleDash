# ==============================
# Stage 1: Base system
# ==============================
FROM python:3.11-slim AS base

# Install system dependencies for Playwright and Node.js
RUN apt-get update && apt-get install -y \
    curl wget gnupg git \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 \
    libasound2 fonts-liberation libxshmfence1 \
    supervisor nodejs npm \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ==============================
# Stage 2: Python dependencies
# ==============================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==============================
# Stage 4: Copy source code
# ==============================
WORKDIR /app
COPY . .

# ==============================
# Stage 5: Playwright setup
# ==============================
RUN python -m playwright install --with-deps chromium

# ==============================
# Stage 6: Supervisor setup
# ==============================
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 3000 5000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
