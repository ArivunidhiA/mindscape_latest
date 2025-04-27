from app import create_app

application = create_app()

# For compatibility with both gunicorn and Flask CLI
app = application 