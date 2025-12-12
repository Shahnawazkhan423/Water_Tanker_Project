# ---------- STAGE 1: build dependencies and install python packages ----------
FROM python:3.11-slim AS builder

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system build dependencies required for some Python packages (psycopg2, Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libmagic-dev \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# copy requirements.txt first to leverage docker cache
COPY requirements.txt /app/requirements.txt

# Install pip packages into a virtual environment location (site-packages)
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r /app/requirements.txt

# ---------- STAGE 2: final runtime image ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # recommended to set your Django settings module via env when running
    DJANGO_SETTINGS_MODULE=Water_Tanker_Project.settings \
    PORT=8000

WORKDIR /app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Install runtime system dependencies (lighter)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    libmagic1 \
 && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/* || (echo "pip install failed" && exit 1)

# Copy project code
COPY . /app

# Ensure ownership for the non-root user
RUN chown -R appuser:appgroup /app

USER appuser

# Expose port
EXPOSE 8000

# Default command:
#  - run migrations
#  - collectstatic (no input)
#  - start gunicorn with 3 workers and binding to 0.0.0.0:8000
#
# NOTE: we run migrate + collectstatic at container start so containers boot ready.
# If you prefer running migrations outside containers, remove the first part.
CMD bash -c "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput --clear && \
    exec gunicorn Water_Tanker_Project.wsgi:application \
      --bind 0.0.0.0:${PORT} \
      --workers 3 \
      --timeout 120 \
      --access-logfile '-' \
      --error-logfile '-' \
      "
