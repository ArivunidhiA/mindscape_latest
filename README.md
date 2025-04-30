# Mindscape - Personal Growth Assessment Platform

Mindscape is a web application that helps users assess and track their personal growth across various dimensions including emotional intelligence, leadership skills, and personal development.

## Features

- User Authentication (Register/Login)
- Interactive Assessments
- Personal Growth Tracking
- Beautiful 3D Animated Interface
- Detailed Results Analysis

## Tech Stack

- Flask (Python Web Framework)
- SQLAlchemy (Database ORM)
- Three.js (3D Animations)
- TailwindCSS (Styling)

## Local Development Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd flask-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

5. Initialize the database and seed initial data:
```bash
python seed_db.py
```

6. Run the development server:
```bash
python run.py
```

The application will be available at http://localhost:5000 with:
- Debug mode enabled
- Auto-reload on code changes
- Development database (dev.db)
- Development-specific configurations

## Project Structure

```
mindscape/
├── app/               # Application package
│   ├── models/       # Database models
│   ├── routes/       # Route handlers
│   ├── templates/    # HTML templates
│   ├── static/       # Static files (CSS, JS, images)
│   └── utils/        # Utility functions
├── config.py         # Configuration settings
├── run.py           # Development server script
└── seed_db.py       # Database initialization script
```

## Deployment

The application is configured for deployment on Render.com:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
4. Set the following environment variables:
   - `FLASK_APP=wsgi.py`
   - `FLASK_ENV=production`
   - `DATABASE_URL` (provided by Render)
   - `SECRET_KEY` (generate a secure random key)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE). 