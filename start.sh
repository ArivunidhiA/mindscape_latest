#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Default port for local development is 8000
if [ -z "${PORT}" ]; then
    export PORT=8000
fi

# Start Gunicorn with minimal configuration and explicitly set worker class to sync
echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn wsgi:app --bind 0.0.0.0:$PORT --worker-class sync 