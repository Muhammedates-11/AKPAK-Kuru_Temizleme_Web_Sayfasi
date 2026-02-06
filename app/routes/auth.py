"""
Authentication routes module.

This module handles user authentication:
- User registration
- Customer login
- Admin login
- Logout
- Password reset
- Password change
"""

import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from app.config import Config
from app.models.database import (
    get_connection,
    create_reset_code,
    verify_reset_code,
)
from app.utils import (
    login_required,
    get_current_user,
    send_email,
    generate_reset_code,
    get_reset_code_expiry,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/giris")
def login():
    """
    Render the login selection page.

    Returns:
        Rendered template: public/giris_sec.html
    """
    return render_template("public/giris_sec.html")


@auth_bp.route("/giris/musteri", methods=["GET", "POST"])
def customer_login():
    """
    Handle customer login.

    GET: Render customer login form
    POST: Process login credentials

    Returns:
        Rendered template or redirect
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("sifre", "")

        if not email or not password:
            flash("Lütfen e-posta ve şifre girin.", "error")
            return render_template("public/giris_musteri.html")

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
                    sifre,
                    rol
                FROM musteriler
                WHERE email=%s
                """,
                (email,),
            )
            user = cursor.fetchone()

            if not user or user["sifre"] != password:
                flash("E-posta veya şifre hatalı.", "error")
                return render_template("public/giris_musteri.html")

            if user["rol"] == "admin":
                flash("Bu hesap yönetici hesabıdır. Yönetici girişi sayfasını kullanın.", "error")
                return render_template("public/giris_musteri.html")

            session["user_id"] = user["musteri_id"]
            session["user_ad"] = user["ad_soyad"]
            session["is_admin"] = False

            logger.info(f"Customer logged in: {email}")
            flash("Giriş başarılı.", "success")
            return redirect(url_for("public.index"))
        except Exception as e:
            logger.error(f"Error during customer login: {e}")
            flash("Giriş yapılırken bir hata oluştu. Lütfen tekrar deneyin.", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("public/giris_musteri.html")


@auth_bp.route("/giris/yonetici", methods=["GET", "POST"])
def admin_login():
    """
    Handle admin login.

    GET: Render admin login form
    POST: Process admin login credentials

    Returns:
        Rendered template or redirect
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("sifre", "")

        if not email or not password:
            flash("Lütfen e-posta ve şifre girin.", "error")
            return render_template("public/giris_admin.html")

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
                    sifre,
                    rol
                FROM musteriler
                WHERE email=%s
                """,
                (email,),
            )
            user = cursor.fetchone()

            if not user or user["sifre"] != password:
                flash("E-posta veya şifre hatalı.", "error")
                return render_template("public/giris_admin.html")

            if user["rol"] != "admin" or user["email"] != Config.ADMIN_EMAIL:
                flash("Bu hesap yönetici yetkisine sahip değil.", "error")
                return render_template("public/giris_admin.html")

            session["user_id"] = user["musteri_id"]
            session["user_ad"] = user["ad_soyad"]
            session["is_admin"] = True

            logger.info(f"Admin logged in: {email}")
            flash("Yönetici girişi başarılı.", "success")
            return redirect(url_for("admin.dashboard"))
        except Exception as e:
            logger.error(f"Error during admin login: {e}")
            flash("Giriş yapılırken bir hata oluştu. Lütfen tekrar deneyin.", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("public/giris_admin.html")


@auth_bp.route("/uye-ol", methods=["GET", "POST"])
def register():
    """
    Handle user registration.

    GET: Render registration form
    POST: Process registration data

    Returns:
        Rendered template or redirect
    """
    form_values = {"ad": "", "soyad": "", "email": "", "telefon": ""}

    if request.method == "POST":
        first_name = request.form.get("ad", "").strip()
        last_name = request.form.get("soyad", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("telefon", "").strip()
        password = request.form.get("sifre", "")

        form_values.update({
            "ad": first_name,
            "soyad": last_name,
            "email": email,
            "telefon": phone
        })

        if not all([first_name, last_name, email, phone, password]):
            flash("Lütfen tüm alanları doldurun.", "error")
            return render_template("public/uye_ol.html", form_values=form_values)

        if len(password) < Config.MIN_PASSWORD_LENGTH:
            flash(f"Şifre en az {Config.MIN_PASSWORD_LENGTH} karakter olmalıdır.", "error")
            return render_template("public/uye_ol.html", form_values=form_values)

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Check if email already exists
            cursor.execute("SELECT 1 FROM musteriler WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("Bu e-posta ile zaten hesap var.", "error")
                return render_template("public/uye_ol.html", form_values=form_values)

            # Check if phone already exists
            cursor.execute("SELECT 1 FROM musteriler WHERE telefon=%s", (phone,))
            if cursor.fetchone():
                flash("Bu telefon numarası ile zaten hesap var.", "error")
                return render_template("public/uye_ol.html", form_values=form_values)

            full_name = f"{first_name} {last_name}"

            cursor.execute(
                """
                INSERT INTO musteriler (ad_soyad, telefon, email, kayit_tarihi, sifre, rol)
                VALUES (%s, %s, %s, NOW(), %s, 'musteri')
                """,
                (full_name, phone, email, password),
            )
            conn.commit()

            logger.info(f"New user registered: {email}")
            flash("Üyelik kaydınız oluşturuldu. Giriş yapabilirsiniz.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            if conn:
                conn.rollback()
            flash("Kayıt işlemi sırasında bir hata oluştu. Lütfen tekrar deneyin.", "error")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("public/uye_ol.html", form_values=form_values)


@auth_bp.route("/cikis")
def logout():
    """
    Handle user logout.

    Clears session and redirects to home page.

    Returns:
        Redirect to home page
    """
    session.clear()
    flash("Çıkış yapıldı.", "info")
    return redirect(url_for("public.index"))


@auth_bp.route("/panel")
@login_required
def panel():
    """
    Render user dashboard panel.

    Returns:
        Rendered template: public/panel.html
    """
    try:
        user = get_current_user()
        notifications = []
        return render_template("public/panel.html", user=user, bildirimler=notifications)
    except Exception as e:
        logger.error(f"Error rendering panel: {e}")
        flash("Panel yüklenirken bir hata oluştu.", "error")
        return redirect(url_for("public.index"))


@auth_bp.route("/sifre-degistir", methods=["POST"])
@login_required
def change_password():
    """
    Handle password change from user panel.

    Returns:
        Redirect to panel
    """
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    new_password2 = request.form.get("new_password2", "")

    if not all([current_password, new_password, new_password2]):
        flash("Lütfen tüm alanları doldurun.", "error")
        return redirect(url_for("auth.panel"))

    if new_password != new_password2:
        flash("Yeni şifreler eşleşmiyor.", "error")
        return redirect(url_for("auth.panel"))

    if len(new_password) < Config.MIN_PASSWORD_LENGTH:
        flash(f"Şifre en az {Config.MIN_PASSWORD_LENGTH} karakter olmalıdır.", "error")
        return redirect(url_for("auth.panel"))

    user = get_current_user()
    if not user:
        flash("Kullanıcı bilgisi bulunamadı.", "error")
        return redirect(url_for("auth.panel"))

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT sifre FROM musteriler WHERE musteri_id=%s",
            (user["musteri_id"],)
        )
        row = cursor.fetchone()

        if not row or row["sifre"] != current_password:
            flash("Mevcut şifreniz hatalı.", "error")
            return redirect(url_for("auth.panel"))

        cursor.execute(
            "UPDATE musteriler SET sifre=%s WHERE musteri_id=%s",
            (new_password, user["musteri_id"])
        )
        conn.commit()

        logger.info(f"Password changed for user {user['customer_id']}")
        flash("Şifreniz güncellendi.", "success")
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        if conn:
            conn.rollback()
        flash("Şifre değiştirilirken bir hata oluştu.", "error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("auth.panel"))


@auth_bp.route("/sifre-unuttum", methods=["GET", "POST"])
def forgot_password():
    """
    Handle password reset process (3-step process).

    Step 1: Request reset (email/phone)
    Step 2: Verify reset code
    Step 3: Set new password

    Returns:
        Rendered template or redirect
    """
    step = request.args.get("step", "1")
    user_id = request.args.get("uid")

    # Step 1: Request reset code
    if step == "1":
        if request.method == "POST":
            identifier = (
                request.form.get("email")
                or request.form.get("identifier")
                or request.form.get("telefon")
                or ""
            ).strip()

            if not identifier:
                flash("Lütfen e-posta veya telefon girin.", "error")
                return render_template("public/sifre_unuttum.html", step=1)

            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    """
                    SELECT musteri_id, email
                    FROM musteriler
                    WHERE email=%s OR telefon=%s
                    LIMIT 1
                    """,
                    (identifier, identifier),
                )
                user_row = cursor.fetchone()

                if not user_row:
                    flash("Girilen bilgiye sahip kullanıcı bulunamadı.", "error")
                    return render_template("public/sifre_unuttum.html", step=1)

                if not user_row.get("email"):
                    flash("Bu kullanıcıda e-posta kayıtlı değil. Admin ile iletişime geçin.", "error")
                    return render_template("public/sifre_unuttum.html", step=1)

                reset_code = generate_reset_code()
                expires_at = get_reset_code_expiry()

                if create_reset_code(user_row["musteri_id"], reset_code, expires_at):
                    try:
                        send_email(
                            to_email=user_row["email"],
                            subject="AKPAK - Şifre Sıfırlama Kodu",
                            body=f"Şifre sıfırlama kodunuz: {reset_code}\n\nKod {Config.RESET_CODE_EXPIRY_MINUTES} dakika geçerlidir.",
                        )
                        flash("Doğrulama kodu e-posta adresinize gönderildi.", "success")
                        return redirect(url_for("auth.forgot_password", step=2, uid=user_row["musteri_id"]))
                    except Exception as e:
                        logger.error(f"Error sending reset email: {e}")
                        flash("Doğrulama kodu gönderilemedi. SMTP ayarlarını kontrol edin.", "error")
                else:
                    flash("Doğrulama kodu oluşturulamadı. Lütfen tekrar deneyin.", "error")
            except Exception as e:
                logger.error(f"Error in password reset step 1: {e}")
                flash("İşlem sırasında bir hata oluştu. Lütfen tekrar deneyin.", "error")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        return render_template("public/sifre_unuttum.html", step=1)

    # Step 2: Verify reset code
    if step == "2":
        if not user_id:
            return redirect(url_for("auth.forgot_password", step=1))

        if request.method == "POST":
            code = (request.form.get("kod") or "").strip()
            if not code:
                flash("Lütfen doğrulama kodunu girin.", "error")
                return render_template("public/sifre_unuttum.html", step=2, uid=user_id)

            if verify_reset_code(int(user_id), code):
                session["pw_reset_uid"] = int(user_id)
                session["pw_reset_ok"] = True
                flash("Kod doğrulandı. Yeni şifrenizi belirleyin.", "success")
                return redirect(url_for("auth.forgot_password", step=3))
            else:
                flash("Kod hatalı veya süresi geçmiş.", "error")

        return render_template("public/sifre_unuttum.html", step=2, uid=user_id)

    # Step 3: Set new password
    if step == "3":
        if not session.get("pw_reset_ok") or not session.get("pw_reset_uid"):
            return redirect(url_for("auth.forgot_password", step=1))

        if request.method == "POST":
            new_password = request.form.get("new_password", "")
            new_password2 = request.form.get("new_password2", "")

            if not new_password or not new_password2:
                flash("Lütfen tüm alanları doldurun.", "error")
                return render_template("public/sifre_unuttum.html", step=3)

            if new_password != new_password2:
                flash("Şifreler eşleşmiyor.", "error")
                return render_template("public/sifre_unuttum.html", step=3)

            if len(new_password) < Config.MIN_PASSWORD_LENGTH:
                flash(f"Şifre en az {Config.MIN_PASSWORD_LENGTH} karakter olmalıdır.", "error")
                return render_template("public/sifre_unuttum.html", step=3)

            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE musteriler SET sifre=%s WHERE musteri_id=%s",
                    (new_password, session["pw_reset_uid"]),
                )
                conn.commit()

                logger.info(f"Password reset completed for user {session['pw_reset_uid']}")
                session.pop("pw_reset_uid", None)
                session.pop("pw_reset_ok", None)

                flash("Şifreniz güncellendi. Şimdi giriş yapabilirsiniz.", "success")
                return redirect(url_for("auth.login"))
            except Exception as e:
                logger.error(f"Error resetting password: {e}")
                if conn:
                    conn.rollback()
                flash("Şifre güncellenirken bir hata oluştu.", "error")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        return render_template("public/sifre_unuttum.html", step=3)

    return redirect(url_for("auth.forgot_password", step=1))

