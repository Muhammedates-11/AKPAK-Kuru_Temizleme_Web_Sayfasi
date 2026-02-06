"""
Admin routes module.

This module handles admin panel operations:
- Dashboard
- Order management
- Customer management
- Branch management
- Price management
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for

from app.config import Config
from app.models.database import (
    get_connection,
    get_all_customers,
    get_all_orders,
    get_dashboard_summary,
    get_orders_paginated,
    get_order_count,
    load_prices,
    upsert_price,
)
from app.utils import (
    admin_required,
    BASE_PRODUCT_PRICES,
    SERVICE_EXTRA_CHARGES,
    LAUNDRY_BAG_PRICE,
    PRODUCT_LABELS,
    SERVICE_LABELS,
    ORDER_STATUS_OPTIONS,
    ORDER_STATUS_MESSAGES,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@admin_required
def dashboard():
    """
    Render admin dashboard with statistics and recent orders.

    Returns:
        Rendered template: dashboard.html
    """
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1

    if page < 1:
        page = 1

    per_page = Config.ORDERS_PER_PAGE

    try:
        summary = get_dashboard_summary()
        from app.models.database import get_contact_messages
        messages = get_contact_messages()
        orders = get_orders_paginated(page, per_page)
        total_orders = get_order_count()
        total_pages = (total_orders + per_page - 1) // per_page if total_orders else 1

        return render_template(
            "dashboard.html",
            toplam_musteri=summary.get("toplam_musteri", 0),
            toplam_siparis=summary.get("toplam_siparis", 0),
            toplam_ciro=summary.get("toplam_ciro", 0.0),
            messages=messages,
            siparisler=orders,
            page=page,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"Error rendering admin dashboard: {e}")
        flash("Dashboard yüklenirken bir hata oluştu.", "error")
        return redirect(url_for("public.index"))


@admin_bp.route("/musteriler-sayfa")
@admin_required
def customers_page():
    """
    Render customer management page.

    Returns:
        Rendered template: musteriler.html
    """
    try:
        customers = get_all_customers()
        return render_template("musteriler.html", musteriler=customers)
    except Exception as e:
        logger.error(f"Error rendering customers page: {e}")
        flash("Müşteriler yüklenirken bir hata oluştu.", "error")
        return redirect(url_for("admin.dashboard"))


@admin_bp.route("/siparisler-sayfa")
@admin_required
def orders_page():
    """
    Render order management page with pagination.

    Returns:
        Rendered template: siparisler.html
    """
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1

    if page < 1:
        page = 1

    per_page = Config.ORDERS_PER_PAGE

    try:
        orders = get_orders_paginated(page, per_page)
        total_orders = get_order_count()
        total_pages = (total_orders + per_page - 1) // per_page if total_orders else 1

        for order in orders:
            status_key = (order.get("durum") or "").upper()
            order["durum_mesaji"] = ORDER_STATUS_MESSAGES.get(status_key, "Sipariş işleniyor.")

        return render_template(
            "siparisler.html",
            siparisler=orders,
            page=page,
            total_pages=total_pages,
            durum_secenekleri=ORDER_STATUS_OPTIONS,
        )
    except Exception as e:
        logger.error(f"Error rendering orders page: {e}")
        flash("Siparişler yüklenirken bir hata oluştu.", "error")
        return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/siparis-durum/<int:order_id>", methods=["POST"])
@admin_required
def update_order_status(order_id: int):
    """
    Update order status.

    Args:
        order_id: Order ID to update

    Returns:
        Redirect to orders page
    """
    new_status = (request.form.get("durum") or "").strip().upper()
    page = request.form.get("page", "1")

    if new_status not in ORDER_STATUS_OPTIONS:
        flash("Geçersiz durum seçimi.", "error")
        return redirect(url_for("admin.orders_page", page=page))

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE siparisler SET durum=%s WHERE siparis_id=%s",
            (new_status, order_id)
        )
        conn.commit()

        logger.info(f"Order {order_id} status updated to {new_status}")
        flash(f"Sipariş SP-{order_id} güncellendi.", "success")
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        if conn:
            conn.rollback()
        flash("Sipariş durumu güncellenirken bir hata oluştu.", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("admin.orders_page", page=page))


@admin_bp.route("/admin/subeler", methods=["GET", "POST"])
@admin_required
def manage_branches():
    """
    Handle branch management (add, update, delete).

    GET: Render branch management page
    POST: Process branch operations

    Returns:
        Rendered template: admin_subeler.html
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == "POST":
            action = request.form.get("action")

            if action == "add":
                name = request.form.get("ad", "").strip()
                city = request.form.get("sehir", "").strip()
                address = request.form.get("adres", "").strip() or None
                phone = request.form.get("telefon", "").strip() or None
                active = 1 if request.form.get("aktif") == "on" else 0

                if not name or not city:
                    flash("Şube eklerken ad ve şehir zorunludur.", "error")
                else:
                    cursor.execute(
                        """
                        INSERT INTO subeler (ad, sehir, adres, telefon, aktif)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (name, city, address, phone, active),
                    )
                    conn.commit()
                    logger.info(f"Branch added: {name} in {city}")
                    flash("Yeni şube eklendi.", "success")

            elif action == "update":
                branch_id = request.form.get("sube_id")
                name = request.form.get("ad", "").strip()
                city = request.form.get("sehir", "").strip()
                address = request.form.get("adres", "").strip() or None
                phone = request.form.get("telefon", "").strip() or None
                active_raw = request.form.get("aktif")
                active = 1 if active_raw in ("on", "1", "true", "True", "YES", "yes") else 0

                if branch_id and name and city:
                    cursor.execute(
                        """
                        UPDATE subeler
                        SET ad=%s, sehir=%s, adres=%s, telefon=%s, aktif=%s
                        WHERE sube_id=%s
                        """,
                        (name, city, address, phone, active, branch_id),
                    )
                    conn.commit()
                    logger.info(f"Branch {branch_id} updated")
                    flash("Şube bilgileri güncellendi.", "success")
                else:
                    flash("Şube güncellerken zorunlu alanlar eksik.", "error")

            elif action == "delete":
                branch_id = request.form.get("sube_id")
                if branch_id:
                    cursor.execute(
                        "UPDATE subeler SET aktif=0 WHERE sube_id=%s",
                        (branch_id,)
                    )
                    conn.commit()
                    logger.info(f"Branch {branch_id} deactivated")
                    flash("Şube pasife alındı (silinmedi).", "success")

        cursor.execute(
            """
            SELECT
                sube_id,
                ad,
                sehir,
                adres,
                telefon,
                aktif
            FROM subeler
            ORDER BY sehir, ad
            """
        )
        branches = cursor.fetchall()
        return render_template("admin_subeler.html", subeler=branches)
    except Exception as e:
        logger.error(f"Error managing branches: {e}")
        if conn:
            conn.rollback()
        flash("Şube işlemleri sırasında bir hata oluştu.", "error")
        return redirect(url_for("admin.dashboard"))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@admin_bp.route("/admin/fiyatlar", methods=["GET", "POST"])
@admin_required
def manage_prices():
    """
    Handle price management (product prices, service charges, bag price).

    GET: Render price management page
    POST: Update prices in database

    Returns:
        Rendered template: admin_fiyatlar.html
    """
    # Load current prices from database
    try:
        product_prices, service_prices, bag_price = load_prices(
            BASE_PRODUCT_PRICES,
            SERVICE_EXTRA_CHARGES,
            LAUNDRY_BAG_PRICE
        )
    except Exception as e:
        logger.error(f"Error loading prices: {e}")
        product_prices = BASE_PRODUCT_PRICES.copy()
        service_prices = SERVICE_EXTRA_CHARGES.copy()
        bag_price = LAUNDRY_BAG_PRICE

    if request.method == "POST":
        # Update product prices
        for key in list(product_prices.keys()):
            value = (request.form.get(f"urun_{key}", "") or "").strip()
            if value:
                try:
                    product_prices[key] = float(value.replace(",", "."))
                except ValueError:
                    pass

        # Update service prices
        for key in list(service_prices.keys()):
            if key == "yok":
                continue
            value = (request.form.get(f"hizmet_{key}", "") or "").strip()
            if value:
                try:
                    service_prices[key] = float(value.replace(",", "."))
                except ValueError:
                    pass

        # Update bag price
        bag_price_value = (request.form.get("file_fiyat", "") or "").strip()
        if bag_price_value:
            try:
                bag_price = float(bag_price_value.replace(",", "."))
            except ValueError:
                pass

        # Save to database
        try:
            for key, value in product_prices.items():
                upsert_price("urun", key, float(value))
            for key, value in service_prices.items():
                upsert_price("hizmet", key, float(value))
            upsert_price("file", "file", float(bag_price))

            logger.info("Prices updated in database")
            flash("Fiyat ayarları kaydedildi (kalıcı).", "success")
        except Exception as e:
            logger.error(f"Error saving prices to database: {e}")
            flash("Fiyatlar güncellendi ama DB'ye kaydedilemedi.", "warning")

        return redirect(url_for("admin.manage_prices"))

    return render_template(
        "admin_fiyatlar.html",
        urun_fiyatlari=product_prices,
        hizmet_ek=service_prices,
        file_fiyat=bag_price,
        urun_etiketleri=PRODUCT_LABELS,
        hizmet_etiketleri=SERVICE_LABELS,
    )


@admin_bp.route("/health")
def health():
    """
    Health check endpoint for monitoring.

    Returns:
        JSON response with status
    """
    return {"status": "ok"}


@admin_bp.route("/musteriler")
def customers_api():
    """
    API endpoint to get all customers (JSON).

    Returns:
        JSON response with customer list
    """
    from flask import jsonify
    try:
        customers = get_all_customers()
        return jsonify(customers)
    except Exception as e:
        logger.error(f"Error in customers API: {e}")
        return jsonify({"error": "Failed to fetch customers"}), 500


@admin_bp.route("/siparisler")
def orders_api():
    """
    API endpoint to get all orders (JSON).

    Returns:
        JSON response with order list
    """
    from flask import jsonify
    try:
        orders = get_all_orders()
        return jsonify(orders)
    except Exception as e:
        logger.error(f"Error in orders API: {e}")
        return jsonify({"error": "Failed to fetch orders"}), 500

