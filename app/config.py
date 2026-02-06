"""
Application configuration module.

This module handles environment variables and application settings.
All sensitive information is loaded from .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""

    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # Database Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "kuru_temizleme")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))

    # SMTP Configuration (for password reset emails)
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "")

    # Admin Configuration
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")

    # Application Settings
    ORDERS_PER_PAGE = int(os.getenv("ORDERS_PER_PAGE", "5"))
    RESET_CODE_EXPIRY_MINUTES = int(os.getenv("RESET_CODE_EXPIRY_MINUTES", "10"))
    MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))


