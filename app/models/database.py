"""
Database operations module.

This module handles all database interactions including:
- Connection management
- Customer operations
- Order operations
- Branch operations
- Price management
- Password reset operations
"""

import logging
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, List, Any, Tuple

from app.config import Config

# Configure logging
logger = logging.getLogger(__name__)


def get_connection():
    """
    Create and return a MySQL database connection.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object

    Raises:
        Error: If connection to database fails
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            autocommit=False
        )
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def get_all_customers() -> List[Dict[str, Any]]:
    """
    Retrieve all customers from the database.

    Returns:
        List[Dict[str, Any]]: List of customer dictionaries with keys:
            - customer_id (musteri_id)
            - full_name (ad_soyad)
            - email
            - phone (telefon)
            - registration_date (kayit_tarihi)
            - role (rol)
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                musteri_id AS customer_id,
                ad_soyad AS full_name,
                email,
                telefon AS phone,
                kayit_tarihi AS registration_date,
                rol AS role
            FROM musteriler
            ORDER BY kayit_tarihi DESC
            """
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        logger.error(f"Error fetching all customers: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_orders() -> List[Dict[str, Any]]:
    """
    Retrieve all orders with customer information and total amount.

    Returns:
        List[Dict[str, Any]]: List of order dictionaries with customer details
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                s.siparis_id AS order_id,
                s.siparis_tarihi AS order_date,
                s.durum AS status,
                s.odeme_yontemi AS payment_method,
                s.aciklama AS description,
                m.ad_soyad AS customer_name,
                m.telefon AS phone,
                COALESCE(SUM(so.adet * so.birim_fiyat), 0) AS total_amount
            FROM siparisler s
            JOIN musteriler m ON m.musteri_id = s.musteri_id
            LEFT JOIN siparis_ogeleri so ON so.siparis_id = s.siparis_id
            GROUP BY
                s.siparis_id,
                s.siparis_tarihi,
                s.durum,
                s.odeme_yontemi,
                s.aciklama,
                m.ad_soyad,
                m.telefon
            ORDER BY s.siparis_tarihi DESC
            """
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        logger.error(f"Error fetching all orders: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_dashboard_summary() -> Dict[str, Any]:
    """
    Get summary statistics for the admin dashboard.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - total_customers (toplam_musteri)
            - total_orders (toplam_siparis)
            - total_revenue (toplam_ciro)
            - recent_orders (son_siparisler)
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Total customers
        cursor.execute("SELECT COUNT(*) AS count FROM musteriler")
        total_customers = cursor.fetchone()["count"]

        # Total orders
        cursor.execute("SELECT COUNT(*) AS count FROM siparisler")
        total_orders = cursor.fetchone()["count"]

        # Total revenue
        cursor.execute(
            """
            SELECT COALESCE(SUM(adet * birim_fiyat), 0) AS total
            FROM siparis_ogeleri
            """
        )
        total_revenue = float(cursor.fetchone()["total"])

        # Recent orders (last 5)
        cursor.execute(
            """
            SELECT
                s.siparis_id AS order_id,
                s.siparis_tarihi AS order_date,
                s.durum AS status,
                s.odeme_yontemi AS payment_method,
                m.ad_soyad AS customer_name,
                COALESCE(SUM(so.adet * so.birim_fiyat), 0) AS total_amount
            FROM siparisler s
            JOIN musteriler m ON m.musteri_id = s.musteri_id
            LEFT JOIN siparis_ogeleri so ON so.siparis_id = s.siparis_id
            GROUP BY
                s.siparis_id,
                s.siparis_tarihi,
                s.durum,
                s.odeme_yontemi,
                m.ad_soyad
            ORDER BY s.siparis_tarihi DESC
            LIMIT 5
            """
        )
        recent_orders = cursor.fetchall()

        return {
            "toplam_musteri": total_customers,
            "toplam_siparis": total_orders,
            "toplam_ciro": total_revenue,
            "son_siparisler": recent_orders,
        }
    except Error as e:
        logger.error(f"Error fetching dashboard summary: {e}")
        return {
            "toplam_musteri": 0,
            "toplam_siparis": 0,
            "toplam_ciro": 0.0,
            "son_siparisler": [],
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def save_contact_message(name: Optional[str], email: Optional[str], message: str) -> bool:
    """
    Save a contact form message to the database.

    Args:
        name: Sender's name (optional)
        email: Sender's email (optional)
        message: Message content (required)

    Returns:
        bool: True if message was saved successfully, False otherwise
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iletisim_mesajlari (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ad VARCHAR(255) NULL,
                email VARCHAR(255) NULL,
                mesaj TEXT NOT NULL,
                tarih DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            INSERT INTO iletisim_mesajlari (ad, email, mesaj)
            VALUES (%s, %s, %s)
            """,
            (name, email, message),
        )
        conn.commit()
        logger.info(f"Contact message saved from {email or 'anonymous'}")
        return True
    except Error as e:
        logger.error(f"Error saving contact message: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_contact_messages() -> List[Dict[str, Any]]:
    """
    Retrieve all contact messages from the database.

    Returns:
        List[Dict[str, Any]]: List of contact message dictionaries
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Create table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS iletisim_mesajlari (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ad VARCHAR(255) NULL,
                email VARCHAR(255) NULL,
                mesaj TEXT NOT NULL,
                tarih DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            SELECT id, ad AS name, email, mesaj AS message, tarih AS date
            FROM iletisim_mesajlari
            ORDER BY tarih DESC
            """
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        logger.error(f"Error fetching contact messages: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_orders_by_customer(customer_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all orders for a specific customer.

    Args:
        customer_id: Customer ID (musteri_id)

    Returns:
        List[Dict[str, Any]]: List of order dictionaries with branch information
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                s.siparis_id,
                s.siparis_tarihi,
                s.durum,
                s.odeme_yontemi,
                s.aciklama,
                COALESCE(SUM(so.adet * so.birim_fiyat), 0) AS toplam_tutar,
                su.sehir,
                su.ad AS sube_adi,
                su.adres AS sube_adres,
                su.telefon AS sube_telefon
            FROM siparisler s
            JOIN subeler su ON su.sube_id = s.sube_id
            LEFT JOIN siparis_ogeleri so ON so.siparis_id = s.siparis_id
            WHERE s.musteri_id = %s
            GROUP BY
                s.siparis_id,
                s.siparis_tarihi,
                s.durum,
                s.odeme_yontemi,
                s.aciklama,
                su.sehir,
                su.ad,
                su.adres,
                su.telefon
            ORDER BY s.siparis_tarihi DESC
            """,
            (customer_id,),
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        logger.error(f"Error fetching orders for customer {customer_id}: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_orders_paginated(page: int, per_page: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve orders with pagination support.

    Args:
        page: Page number (1-indexed)
        per_page: Number of orders per page

    Returns:
        List[Dict[str, Any]]: List of order dictionaries for the requested page
    """
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 5

    offset = (page - 1) * per_page
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
            cursor.execute(
            """
            SELECT
                s.siparis_id,
                s.siparis_tarihi,
                s.durum,
                s.odeme_yontemi,
                s.aciklama,
                m.ad_soyad AS musteri_adi,
                m.telefon,
                COALESCE(SUM(so.adet * so.birim_fiyat), 0) AS toplam_tutar,
                su.sehir AS sube_sehir,
                su.ad AS sube_adi
            FROM siparisler s
            JOIN musteriler m ON m.musteri_id = s.musteri_id
            LEFT JOIN siparis_ogeleri so ON so.siparis_id = s.siparis_id
            LEFT JOIN subeler su ON su.sube_id = s.sube_id
            GROUP BY
                s.siparis_id,
                s.siparis_tarihi,
                s.durum,
                s.odeme_yontemi,
                s.aciklama,
                m.ad_soyad,
                m.telefon,
                su.sehir,
                su.ad
            ORDER BY s.siparis_tarihi DESC
            LIMIT %s OFFSET %s
            """,
            (per_page, offset),
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        logger.error(f"Error fetching paginated orders: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_order_count() -> int:
    """
    Get total count of orders in the database.

    Returns:
        int: Total number of orders
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM siparisler")
        count = cursor.fetchone()[0]
        return int(count)
    except Error as e:
        logger.error(f"Error getting order count: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_branches(only_active: bool = True) -> List[Dict[str, Any]]:
    """
    Retrieve branches from the database.

    Args:
        only_active: If True, return only active branches

    Returns:
        List[Dict[str, Any]]: List of branch dictionaries
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if only_active:
            cursor.execute(
                """
                SELECT
                    sube_id AS branch_id,
                    ad AS name,
                    sehir AS city,
                    adres AS address,
                    telefon AS phone,
                    aktif AS active
                FROM subeler
                WHERE aktif = 1
                ORDER BY sehir, ad
                """
            )
        else:
            cursor.execute(
                """
                SELECT
                    sube_id AS branch_id,
                    ad AS name,
                    sehir AS city,
                    adres AS address,
                    telefon AS phone,
                    aktif AS active
                FROM subeler
                ORDER BY sehir, ad
                """
            )

        rows = cursor.fetchall()
        return rows
    except Error as e:
        logger.error(f"Error fetching branches: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def _ensure_price_table():
    """
    Ensure the price settings table exists in the database.
    Creates the table if it doesn't exist.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fiyat_ayarlari (
                tur VARCHAR(20) NOT NULL,
                anahtar VARCHAR(64) NOT NULL,
                deger DECIMAL(10,2) NOT NULL,
                guncellendi TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (tur, anahtar)
            )
            """
        )
        conn.commit()
    except Error as e:
        logger.error(f"Error ensuring price table exists: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def upsert_price(price_type: str, key: str, value: float) -> bool:
    """
    Insert or update a price setting in the database.

    Args:
        price_type: Type of price (e.g., 'urun', 'hizmet', 'file')
        key: Price key identifier
        value: Price value

    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    cursor = None
    try:
        _ensure_price_table()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO fiyat_ayarlari (tur, anahtar, deger)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE deger=VALUES(deger)
            """,
            (price_type, key, value),
        )
        conn.commit()
        return True
    except Error as e:
        logger.error(f"Error upserting price: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def load_prices(
    default_product_prices: dict,
    default_service_prices: dict,
    default_file_price: float
) -> Tuple[dict, dict, float]:
    """
    Load prices from database, using defaults if not found.

    Args:
        default_product_prices: Default product prices dictionary
        default_service_prices: Default service prices dictionary
        default_file_price: Default file price

    Returns:
        Tuple[dict, dict, float]: (product_prices, service_prices, file_price)
    """
    product_prices = dict(default_product_prices)
    service_prices = dict(default_service_prices)
    file_price = float(default_file_price)

    conn = None
    cursor = None
    try:
        _ensure_price_table()
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT tur, anahtar, deger FROM fiyat_ayarlari")
        rows = cursor.fetchall()

        for row in rows:
            price_type = (row["tur"] or "").lower()
            key = row["anahtar"]
            value = float(row["deger"])

            if price_type == "urun" and key in product_prices:
                product_prices[key] = value
            elif price_type == "hizmet" and key in service_prices:
                service_prices[key] = value
            elif price_type == "file" and key == "file":
                file_price = value

        return product_prices, service_prices, file_price
    except Error as e:
        logger.error(f"Error loading prices: {e}")
        return product_prices, service_prices, file_price
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def _ensure_reset_table():
    """
    Ensure the password reset codes table exists in the database.
    Creates the table if it doesn't exist.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sifre_sifirlama_kodlari (
                id INT AUTO_INCREMENT PRIMARY KEY,
                musteri_id INT NOT NULL,
                kod VARCHAR(10) NOT NULL,
                expires_at DATETIME NOT NULL,
                used TINYINT(1) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_musteri (musteri_id),
                CONSTRAINT fk_reset_musteri
                    FOREIGN KEY (musteri_id) REFERENCES musteriler(musteri_id)
                    ON DELETE CASCADE
            )
            """
        )
        conn.commit()
    except Error as e:
        logger.error(f"Error ensuring reset table exists: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def create_reset_code(customer_id: int, code: str, expires_at) -> bool:
    """
    Create a password reset code for a customer.

    Args:
        customer_id: Customer ID (musteri_id)
        code: Reset code string
        expires_at: Expiration datetime

    Returns:
        bool: True if successful, False otherwise
    """
    conn = None
    cursor = None
    try:
        _ensure_reset_table()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sifre_sifirlama_kodlari (musteri_id, kod, expires_at, used)
            VALUES (%s, %s, %s, 0)
            """,
            (customer_id, code, expires_at),
        )
        conn.commit()
        logger.info(f"Reset code created for customer {customer_id}")
        return True
    except Error as e:
        logger.error(f"Error creating reset code: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def verify_reset_code(customer_id: int, code: str) -> bool:
    """
    Verify and mark a password reset code as used.

    Args:
        customer_id: Customer ID (musteri_id)
        code: Reset code to verify

    Returns:
        bool: True if code is valid and unused, False otherwise
    """
    conn = None
    cursor = None
    try:
        _ensure_reset_table()
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id
            FROM sifre_sifirlama_kodlari
            WHERE musteri_id=%s AND kod=%s AND used=0 AND expires_at > NOW()
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (customer_id, code),
        )
        row = cursor.fetchone()

        if not row:
            return False

        cursor.execute(
            "UPDATE sifre_sifirlama_kodlari SET used=1 WHERE id=%s",
            (row["id"],)
        )
        conn.commit()
        logger.info(f"Reset code verified for customer {customer_id}")
        return True
    except Error as e:
        logger.error(f"Error verifying reset code: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

