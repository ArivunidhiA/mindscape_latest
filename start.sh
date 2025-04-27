#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Export necessary environment variables
export FLASK_APP=app.py
export FLASK_ENV=production
export PORT=${PORT:-8000}

# Start Gunicorn
echo "Starting Gunicorn..."
python -m gunicorn wsgi:app 