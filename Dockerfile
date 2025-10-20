# Multi-stage: build Tailwind CSS with Node, run Django with Python

# 1) Node stage: build CSS
FROM node:20-alpine AS assets
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY tailwind.config.js postcss.config.js ./
COPY assets ./assets
COPY templates ./templates
COPY core/templates ./core/templates
RUN npm run build

# 2) Python stage: Django app
FROM python:3.12-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Bring in built CSS
COPY --from=assets /app/static/css/styles.css ./static/css/styles.css

# Collect static for production
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Bind to PORT if provided by hosting (e.g., Render/Heroku), default 8000
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
