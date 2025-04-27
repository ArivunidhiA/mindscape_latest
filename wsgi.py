from app import create_app

app = create_app()

# For compatibility with both gunicorn and Flask CLI
application = app 