# ---------- STAGE 1: build dependencies and build wheels ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Build-time packages (dev headers & tools) required to compile wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libmagic-dev \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r /app/requirements.txt

# ---------- STAGE 2: runtime ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=Water_Tanker_Project.settings \
    PORT=8000

WORKDIR /app

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Runtime packages (smaller) — do NOT install dev packages here
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient21 \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    libmagic1 \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install wheels built earlier
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy project files
COPY . /app
RUN chown -R appuser:appgroup /app

USER appuser
EXPOSE 8000

CMD ["bash", "-c", "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput --clear && \
    exec gunicorn Water_Tanker_Project.wsgi:application \
      --bind 0.0.0.0:${PORT} \
      --workers 3 \
      --timeout 120 \
      --access-logfile '-' \
      --error-logfile '-' \
"]
