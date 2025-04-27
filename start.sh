#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Start Gunicorn with correct WSGI application
echo "Starting Gunicorn..."
exec gunicorn "wsgi:app" 