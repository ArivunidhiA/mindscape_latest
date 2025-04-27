#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Export necessary environment variables
export FLASK_APP=app
export FLASK_ENV=production
export PORT=${PORT:-8000}

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --threads 4 --worker-class gthread 