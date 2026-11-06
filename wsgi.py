"""
ApproveHub — WSGI Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Production WSGI entry point for Gunicorn and compatible servers.
Imports the fully configured Flask application from the application factory.

Usage:
    gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4
"""

from app import app

if __name__ == "__main__":
    app.run()
