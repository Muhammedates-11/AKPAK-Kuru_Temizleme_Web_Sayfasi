"""
Public routes module.

This module handles public-facing routes that don't require authentication:
- Home page
- Services page
- Prices page
- Branches page
- Contact page
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for

from app.models.database import get_branches, save_contact_message
from app.utils import (
    BASE_PRODUCT_PRICES,
    SERVICE_EXTRA_CHARGES,
    LAUNDRY_BAG_PRICE,
    PRODUCT_LABELS,
    SERVICE_LABELS,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    """
    Render the home page.

    Returns:
        Rendered template: public/index.html
    """
    return render_template("public/index.html")


@public_bp.route("/hizmetler")
def services():
    """
    Render the services page.

    Returns:
        Rendered template: public/hizmetler.html
    """
    return render_template("public/hizmetler.html")


@public_bp.route("/fiyatlar")
def prices():
    """
    Render the prices page with current pricing information.

    Returns:
        Rendered template: public/fiyatlar.html with price data
    """
    try:
        return render_template(
            "public/fiyatlar.html",
            urun_fiyatlari=BASE_PRODUCT_PRICES,
            hizmet_ek=SERVICE_EXTRA_CHARGES,
            file_fiyat=LAUNDRY_BAG_PRICE,
            urun_etiketleri=PRODUCT_LABELS,
            hizmet_etiketleri=SERVICE_LABELS,
        )
    except Exception as e:
        logger.error(f"Error rendering prices page: {e}")
        flash("Fiyat bilgileri yüklenirken bir hata oluştu.", "error")
        return redirect(url_for("public.index"))


@public_bp.route("/subeler")
def branches():
    """
    Render the branches page with active branches.

    Returns:
        Rendered template: public/subeler.html with branch data
    """
    try:
        branches_list = get_branches(only_active=True)
        return render_template("public/subeler.html", branches=branches_list)
    except Exception as e:
        logger.error(f"Error rendering branches page: {e}")
        flash("Şube bilgileri yüklenirken bir hata oluştu.", "error")
        return redirect(url_for("public.index"))


@public_bp.route("/iletisim", methods=["GET", "POST"])
def contact():
    """
    Handle contact form submission and display.

    GET: Render contact form
    POST: Process and save contact message

    Returns:
        Rendered template: public/iletisim.html
    """
    if request.method == "POST":
        name = request.form.get("ad", "").strip() or None
        email = request.form.get("email", "").strip() or None
        message = request.form.get("mesaj", "").strip()

        if not message:
            flash("Lütfen mesajınızı yazın.", "error")
            return render_template("public/iletisim.html")

        try:
            success = save_contact_message(name, email, message)
            if success:
                flash("Mesajınız gönderildi. Teşekkür ederiz!", "success")
                return redirect(url_for("public.contact"))
            else:
                flash("Mesaj gönderilirken bir hata oluştu. Lütfen tekrar deneyin.", "error")
        except Exception as e:
            logger.error(f"Error processing contact form: {e}")
            flash("Mesaj gönderilirken bir hata oluştu. Lütfen tekrar deneyin.", "error")

    return render_template("public/iletisim.html")


