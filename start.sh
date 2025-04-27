#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set default environment variables if not set
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-2}
export THREADS=${THREADS:-2}
export TIMEOUT=${TIMEOUT:-120}

# Start Gunicorn with basic configuration
echo "Starting Gunicorn..."
exec gunicorn "wsgi:app" \
    --bind "0.0.0.0:$PORT" \
    --workers $WORKERS \
    --threads $THREADS \
    --timeout $TIMEOUT \
    --worker-class gthread 