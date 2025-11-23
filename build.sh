#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Create superuser if environment variables are set
if [ -n "$SUPERUSER_USERNAME" ] && [ -n "$SUPERUSER_PASSWORD" ]; then
    python manage.py create_superuser
fi

# Import services and packages
python manage.py import_services --file data/cleaned_data.json

