#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Export environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Default port for local development is 8000
if [ -z "${PORT}" ]; then
    export PORT=8000
fi

# Kill any existing processes on the port
if command -v lsof >/dev/null 2>&1; then
    lsof -ti:${PORT} | xargs kill -9 2>/dev/null || true
fi

# Start Gunicorn
echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn wsgi:app --bind 0.0.0.0:${PORT} --timeout 120 