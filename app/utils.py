"""
Utility functions and decorators module.

This module contains:
- Authentication decorators (login_required, admin_required)
- Email sending functionality
- User session management
- Order status constants and messages
- Price configuration constants
"""

import logging
import random
import smtplib
from datetime import datetime, timedelta
from functools import wraps
from email.message import EmailMessage
from typing import Optional, Dict, Any

from flask import session, redirect, url_for, flash

from app.config import Config

# Configure logging
logger = logging.getLogger(__name__)

# ============= ORDER STATUS CONSTANTS =============

ORDER_STATUS_OPTIONS = [
    "ALINDI",
    "KURYE YOLDA",
    "HAZIRLANIYOR",
    "TESLIMAT ICIN KURYE YOLA CIKTI",
    "TESLIM EDILDI",
]

ORDER_STATUS_MESSAGES = {
    "ALINDI": "Siparişiniz alındı, kuryemiz yakın zamanda sizden teslim alacaktır.",
    "KURYE YOLDA": "Kuryemiz yola çıktı. Yakında adresinizden teslim alacaktır.",
    "HAZIRLANIYOR": "Siparişiniz işleme alındı, hazırlık aşamasındadır.",
    "TESLIMAT ICIN KURYE YOLA CIKTI": "Teslim edilmek üzere kuryemiz yola çıktı.",
    "TESLIM EDILDI": "Siparişiniz teslim edildi. Bizi tercih ettiğiniz için teşekkürler!",
}

# ============= PRICE CONFIGURATION CONSTANTS =============

BASE_PRODUCT_PRICES = {
    "gomlek": 70,
    "tisort": 60,
    "kazak": 90,
    "pantolon": 100,
    "elbise": 140,
    "mont": 220,
    "takim": 260,
    "corap": 20,
}

PRODUCT_LABELS = {
    "gomlek": "Gömlek",
    "tisort": "Tişört / Crop",
    "kazak": "Kazak / Sweatshirt",
    "pantolon": "Pantolon / Eşofman / Tayt",
    "elbise": "Elbise / Etek",
    "mont": "Mont / Kaban",
    "takim": "Takım Elbise",
    "corap": "Çorap (çift)",
}

SERVICE_EXTRA_CHARGES = {
    "yok": 0,
    "yikama": 0,
    "yikama_kurutma": 10,
    "yikama_kurutma_utu": 30,
    "sadece_utu": 40,
}

SERVICE_LABELS = {
    "yikama": "Sadece Yıkama",
    "yikama_kurutma": "Yıkama + Kurutma",
    "yikama_kurutma_utu": "Yıkama + Kurutma + Ütü",
    "sadece_utu": "Sadece Ütü",
}

LAUNDRY_BAG_PRICE = 300  # Laundry bag price per unit


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current logged-in user from session.

    Returns:
        Optional[Dict[str, Any]]: User dictionary if logged in, None otherwise
    """
    from app.models.database import get_connection

    user_id = session.get("user_id")
    if not user_id:
        return None

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                musteri_id,
                ad_soyad,
                email,
                telefon,
                rol
            FROM musteriler
            WHERE musteri_id = %s
            """,
            (user_id,),
        )
        user = cursor.fetchone()
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def login_required(func):
    """
    Decorator to require user login for a route.

    Redirects to login page if user is not logged in.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Lütfen önce giriş yapın.", "warning")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    """
    Decorator to require admin privileges for a route.

    Redirects to login page if not logged in,
    or to home page if not an admin.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Lütfen önce giriş yapın.", "warning")
            return redirect(url_for("auth.login"))
        if not session.get("is_admin"):
            flash("Bu sayfaya sadece yöneticiler erişebilir.", "error")
            return redirect(url_for("public.index"))
        return func(*args, **kwargs)
    return wrapper


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email using SMTP configuration from environment variables.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content

    Returns:
        bool: True if email sent successfully, False otherwise

    Raises:
        RuntimeError: If SMTP configuration is missing
    """
    if not Config.SMTP_HOST or not Config.SMTP_USER or not Config.SMTP_PASSWORD:
        error_msg = "SMTP settings are missing. Please configure SMTP_HOST, SMTP_USER, and SMTP_PASSWORD in .env"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = Config.SMTP_FROM or Config.SMTP_USER
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return False


def generate_reset_code() -> str:
    """
    Generate a random 6-digit reset code.

    Returns:
        str: 6-digit code as string
    """
    return f"{random.randint(100000, 999999)}"


def get_reset_code_expiry() -> datetime:
    """
    Get the expiry datetime for a reset code.

    Returns:
        datetime: Expiry datetime based on configuration
    """
    return datetime.now() + timedelta(minutes=Config.RESET_CODE_EXPIRY_MINUTES)

