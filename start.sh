#!/bin/bash

# Export necessary environment variables
export FLASK_APP=app
export FLASK_ENV=production
export PORT=${PORT:-8000}

# Start Gunicorn
gunicorn wsgi:app 