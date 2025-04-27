#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set default environment variables if not set
export PORT=${PORT:-8000}

# Start Gunicorn with minimal configuration
echo "Starting Gunicorn..."
exec gunicorn wsgi:app -b 0.0.0.0:$PORT -w 2 