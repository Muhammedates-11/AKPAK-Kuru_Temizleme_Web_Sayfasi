"""
Order routes module.

This module handles order-related operations:
- Order creation
- Order tracking
- Customer order history
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from app.models.database import (
    get_connection,
    get_branches,
    get_orders_by_customer,
)
from app.utils import (
    login_required,
    get_current_user,
    BASE_PRODUCT_PRICES,
    SERVICE_EXTRA_CHARGES,
    LAUNDRY_BAG_PRICE,
    ORDER_STATUS_MESSAGES,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/siparis-olustur", methods=["GET", "POST"])
@login_required
def create_order():
    """
    Handle order creation.

    GET: Render order creation form
    POST: Process and save order

    Returns:
        Rendered template or redirect
    """
    user = get_current_user()

    if session.get("is_admin"):
        flash("Yönetici sipariş oluşturamaz.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        branch = request.form.get("sube", "").strip()
        address = request.form.get("adres", "").strip()
        payment_method = request.form.get("odeme_yontemi", "kapida")
        bag_count = request.form.get("filesi_adedi", "0").strip()

        if not branch or not address:
            flash("Lütfen şube ve adres alanlarını doldurun.", "error")
            return redirect(url_for("orders.create_order"))

        try:
            bag_count_int = int(bag_count) if bag_count else 0
        except ValueError:
            bag_count_int = 0

        total = 0
        if bag_count_int > 0:
            total += bag_count_int * LAUNDRY_BAG_PRICE

        products = [
            ("gomlek", "Gömlek"),
            ("tisort", "Tişört / Crop"),
            ("kazak", "Kazak / Sweatshirt"),
            ("pantolon", "Pantolon / Eşofman / Tayt"),
            ("elbise", "Elbise / Etek"),
            ("mont", "Mont / Kaban"),
            ("takim", "Takım Elbise"),
            ("corap", "Çorap (çift)"),
        ]

        order_details = []

        for key, label in products:
            quantity_raw = request.form.get(f"{key}_adet", "0").strip()
            service_type = request.form.get(f"{key}_hizmet", "yok")

            try:
                quantity = int(quantity_raw) if quantity_raw else 0
            except ValueError:
                quantity = 0

            if quantity <= 0 or service_type == "yok":
                continue

            unit_price = BASE_PRODUCT_PRICES.get(key, 0) + SERVICE_EXTRA_CHARGES.get(service_type, 0)
            subtotal = quantity * unit_price
            total += subtotal
            order_details.append(f"{quantity} x {label} ({service_type.replace('_', ' ')}) = {subtotal} TL")

        if total == 0:
            flash("Lütfen en az bir ürün ya da file seçin.", "error")
            return redirect(url_for("orders.create_order"))

        description_lines = [
            f"Şube: {branch}",
            f"Adres: {address}",
            f"Ödeme yöntemi: {payment_method}",
        ]
        if bag_count_int > 0:
            description_lines.append(f"Çamaşır filesi adedi: {bag_count_int} ({LAUNDRY_BAG_PRICE} TL/adet)")
        description_lines.extend(order_details)
        description_lines.append(f"Tahmini toplam tutar: {total} TL")

        description = "\n".join(description_lines)

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Branch selection (string "City - Name" or direct ID)
            branch_id = None
            if branch.isdigit():
                branch_id = int(branch)
            else:
                if " - " in branch:
                    city, name = [p.strip() for p in branch.split(" - ", 1)]
                else:
                    city = branch.strip()
                    name = branch.strip()

                cursor.execute(
                    """
                    SELECT sube_id AS branch_id
                    FROM subeler
                    WHERE sehir=%s AND ad=%s AND aktif=1
                    LIMIT 1
                    """,
                    (city, name),
                )
                row = cursor.fetchone()

                if row:
                    branch_id = row["branch_id"]
                else:
                    cursor.execute(
                        """
                        INSERT INTO subeler (ad, sehir, adres, telefon, aktif)
                        VALUES (%s, %s, %s, %s, 1)
                        """,
                        (name, city, None, None),
                    )
                    branch_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO siparisler
                  (musteri_id, sube_id, kurye_id, siparis_tarihi, teslim_tarihi,
                   durum, aciklama, odeme_yontemi)
                VALUES (%s, %s, NULL, NOW(), NULL, %s, %s, %s)
                """,
                (user["musteri_id"], branch_id, "ALINDI", description, payment_method),
            )
            order_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO siparis_ogeleri (siparis_id, hizmet_id, adet, birim_fiyat)
                VALUES (%s, NULL, 1, %s)
                """,
                (order_id, total),
            )

            conn.commit()

            logger.info(f"Order created: SP-{order_id} by customer {user['musteri_id']}")
            flash(
                f"Sipariş talebiniz alındı. Sipariş numaranız: SP-{order_id} "
                f"(Tahmini tutar: {total} TL)",
                "success",
            )
            return redirect(url_for("public.index"))
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            if conn:
                conn.rollback()
            flash("Sipariş oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    try:
        branches_list = get_branches(only_active=True)
        return render_template(
            "public/siparis_olustur.html",
            mevcut_ad_soyad=user["ad_soyad"],
            mevcut_telefon=user["telefon"],
            baz_fiyatlar=BASE_PRODUCT_PRICES,
            hizmet_ek=SERVICE_EXTRA_CHARGES,
            file_fiyat=LAUNDRY_BAG_PRICE,
            branches=branches_list,
        )
    except Exception as e:
        logger.error(f"Error rendering order creation form: {e}")
        flash("Sipariş formu yüklenirken bir hata oluştu.", "error")
        return redirect(url_for("public.index"))


@orders_bp.route("/siparis-takip", methods=["GET", "POST"])
def track_order():
    """
    Handle order tracking by order code and phone number.

    GET: Render order tracking form
    POST: Process tracking request

    Returns:
        Rendered template: public/siparis_takip.html
    """
    order_info = None

    if request.method == "POST":
        order_code = request.form.get("siparis_kodu", "").strip()
        phone = request.form.get("telefon", "").strip()

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    s.siparis_id,
                    s.siparis_tarihi,
                    s.durum,
                    m.ad_soyad,
                    m.telefon
                FROM siparisler s
                JOIN musteriler m ON m.musteri_id = s.musteri_id
                WHERE 1=1
            """
            params = []

            if order_code:
                if order_code.upper().startswith("SP-"):
                    try:
                        order_num = int(order_code.split("-")[1])
                        query += " AND s.siparis_id = %s"
                        params.append(order_num)
                    except ValueError:
                        flash("Sipariş numarası formatı hatalı (SP-123 gibi).", "error")
                else:
                    flash("Sipariş numarası SP-123 formatında olmalı.", "error")

            if phone:
                query += " AND m.telefon = %s"
                params.append(phone)

            if params:
                cursor.execute(query, tuple(params))
                order_info = cursor.fetchone()
                if not order_info:
                    flash("Eşleşen sipariş bulunamadı.", "warning")
            else:
                flash("Lütfen sipariş numarası veya telefon girin.", "error")
        except Exception as e:
            logger.error(f"Error tracking order: {e}")
            flash("Sipariş aranırken bir hata oluştu.", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("public/siparis_takip.html", siparis=order_info)


@orders_bp.route("/siparislerim")
@login_required
def my_orders():
    """
    Display all orders for the current logged-in customer.

    Returns:
        Rendered template: public/siparislerim.html
    """
    if session.get("is_admin"):
        return redirect(url_for("admin.dashboard"))

    try:
        user = get_current_user()
        orders = get_orders_by_customer(user["musteri_id"])

        for order in orders:
            if order.get("aciklama"):
                order["aciklama_satirlari"] = [
                    line.strip() for line in order["aciklama"].split("\n") if line.strip()
                ]
            else:
                order["aciklama_satirlari"] = []

            status_key = (order.get("durum") or "").upper()
            order["durum_mesaji"] = ORDER_STATUS_MESSAGES.get(
                status_key,
                "Siparişiniz işleniyor. En kısa sürede bilgilendirileceksiniz.",
            )

        return render_template("public/siparislerim.html", orders=orders)
    except Exception as e:
        logger.error(f"Error fetching customer orders: {e}")
        flash("Siparişler yüklenirken bir hata oluştu.", "error")
        return redirect(url_for("public.index"))

