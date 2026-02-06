"""
Application entry point.

This module starts the Flask development server.
"""

from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    # Run the Flask development server
    # In production, use a WSGI server like Gunicorn
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=Config.DEBUG
    )
