#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Export environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start Gunicorn
exec gunicorn wsgi:app --bind 0.0.0.0:${PORT:-5000} 