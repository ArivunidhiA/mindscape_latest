#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Export necessary environment variables
export FLASK_APP=app
export FLASK_ENV=production
export PORT=${PORT:-8000}

# Start Gunicorn with the recommended command
echo "Starting Gunicorn..."
gunicorn wsgi:app --bind 0.0.0.0:$PORT 