#!/bin/bash

# Export necessary environment variables
export FLASK_APP=app
export FLASK_ENV=production
export PORT=${PORT:-8080}

# Start Gunicorn
gunicorn --bind 0.0.0.0:$PORT application:app 