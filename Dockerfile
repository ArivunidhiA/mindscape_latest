FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080
ENV FLASK_APP=app
ENV FLASK_ENV=production

CMD gunicorn wsgi:app 