import mysql.connector

conn=mysql.connector.connect(
    host="localhost",
    user="  root",  
    password="Ates1111.",  # <-- BURAYI KENDI SIFRENLE DEGISTIR
    database="kuru_temizleme",
)
def get_connection():
    """
    MySQL bağlantısı. Şifre kısmını kendi sistemine göre güncelle.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ates1111.",  # <-- BURAYI KENDI SIFRENLE DEGISTIR
        database="kuru_temizleme",
    )


def get_all_customers():
    """
    Tüm müşterileri listelemek için.
    Admin paneli ve API'de kullanılıyor.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT
            musteri_id,
            ad_soyad,
            email,
            telefon,
            kayit_tarihi,
            rol
        FROM musteriler
        ORDER BY kayit_tarihi DESC;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_all_orders():
    """
    Tüm siparişleri, müşteri adı ve toplam tutarla birlikte döner.
    Admin paneli ve API'de kullanılıyor.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT
            s.siparis_id,
            s.siparis_tarihi,
            s.durum,
            s.odeme_yontemi,
            s.aciklama,
            m.ad_soyad AS musteri_adi,
            m.telefon,
            COALESCE(SUM(so.adet * so.birim_fiyat), 0) AS toplam_tutar
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
        ORDER BY s.siparis_tarihi DESC;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_dashboard_summary():
    """
    Dashboard için özet istatistikler:
    - toplam müşteri
    - toplam sipariş
    - toplam ciro
    - son 5 sipariş
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Toplam müşteri
    cur.execute("SELECT COUNT(*) AS sayi FROM musteriler;")
    toplam_musteri = cur.fetchone()["sayi"]

    # Toplam sipariş
    cur.execute("SELECT COUNT(*) AS sayi FROM siparisler;")
    toplam_siparis = cur.fetchone()["sayi"]

    # Toplam ciro (siparis_ogeleri tablosundan)
    cur.execute(
        """
        SELECT COALESCE(SUM(adet * birim_fiyat), 0) AS toplam
        FROM siparis_ogeleri;
        """
    )
    toplam_ciro = float(cur.fetchone()["toplam"])

    # Son 5 sipariş
    cur.execute(
        """
        SELECT
            s.siparis_id,
            s.siparis_tarihi,
            s.durum,
            s.odeme_yontemi,
            m.ad_soyad AS musteri_adi,
            COALESCE(SUM(so.adet * so.birim_fiyat), 0) AS toplam_tutar
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
        LIMIT 5;
        """
    )
    son_siparisler = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "toplam_musteri": toplam_musteri,
        "toplam_siparis": toplam_siparis,
        "toplam_ciro": toplam_ciro,
        "son_siparisler": son_siparisler,
    }


# ---------------- İletişim Mesajları ----------------
def save_contact_message(ad, email, mesaj):
    """
    İletişim formundan gelen mesajı veritabanına kaydeder.
    Tablo yoksa otomatik oluşturulur.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Tablo oluştur (varsa CREATE TABLE IF NOT EXISTS)
    cur.execute(
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
    cur.execute(
        """
        INSERT INTO iletisim_mesajlari (ad, email, mesaj)
        VALUES (%s, %s, %s)
        """,
        (ad, email, mesaj),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_contact_messages():
    """
    Veritabanındaki tüm iletişim mesajlarını döner.
    Yoksa tabloyu oluşturur.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    # Tablo yoksa oluştur
    cur.execute(
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
    cur.execute(
        "SELECT id, ad, email, mesaj, tarih FROM iletisim_mesajlari ORDER BY tarih DESC"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ---------------- Siparişlerim ----------------
def get_orders_by_customer(musteri_id):
    """
    Belirtilen müşteriye ait tüm siparişleri, şube bilgisi ve toplam tutar ile birlikte döndürür.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
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
        GROUP BY s.siparis_id, s.siparis_tarihi, s.durum, s.odeme_yontemi,
                 s.aciklama, su.sehir, su.ad, su.adres, su.telefon
        ORDER BY s.siparis_tarihi DESC
        """,
        (musteri_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ---------------- Siparişler (Pagination) ----------------
def get_orders_paginated(page: int, per_page: int = 5):
    """
    Tüm siparişleri belirli bir sayfa ve sayfa başı adet ile döndürür.
    """
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 5

    offset = (page - 1) * per_page
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
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
        LIMIT %s OFFSET %s;
        """,
        (per_page, offset),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_order_count() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM siparisler;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return int(count)


# ---------------- Şubeler (Public) ----------------
def get_branches(only_active: bool = True):
    """
    Admin tarafında şubeler yönetilebilir (adres/telefon/aktif vs.).
    Müşteri tarafında /subeler sayfası bu fonksiyonu kullanır.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if only_active:
        cur.execute(
            """
            SELECT sube_id, ad, sehir, adres, telefon, aktif
            FROM subeler
            WHERE aktif = 1
            ORDER BY sehir, ad
            """
        )
    else:
        cur.execute(
            """
            SELECT sube_id, ad, sehir, adres, telefon, aktif
            FROM subeler
            ORDER BY sehir, ad
            """
        )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#   ✅ KALICI FİYATLAR + ŞİFRE SIFIRLAMA (YENİ EKLENDİ)
#   - Tablo yoksa otomatik oluşturur.
# ============================================================

def _ensure_price_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
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
    cur.close()
    conn.close()


def upsert_price(tur: str, anahtar: str, deger: float):
    _ensure_price_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO fiyat_ayarlari (tur, anahtar, deger)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE deger=VALUES(deger)
        """,
        (tur, anahtar, deger),
    )
    conn.commit()
    cur.close()
    conn.close()


def load_prices(default_baz: dict, default_hizmet: dict, default_file: float):
    _ensure_price_table()
    baz = dict(default_baz)
    hizmet = dict(default_hizmet)
    file_fiyat = float(default_file)

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT tur, anahtar, deger FROM fiyat_ayarlari")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    for r in rows:
        t = (r["tur"] or "").lower()
        k = r["anahtar"]
        v = float(r["deger"])

        if t == "urun" and k in baz:
            baz[k] = v
        elif t == "hizmet" and k in hizmet:
            hizmet[k] = v
        elif t == "file" and k == "file":
            file_fiyat = v

    return baz, hizmet, file_fiyat


def _ensure_reset_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
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
    cur.close()
    conn.close()


def create_reset_code(musteri_id: int, kod: str, expires_at):
    _ensure_reset_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sifre_sifirlama_kodlari (musteri_id, kod, expires_at, used)
        VALUES (%s, %s, %s, 0)
        """,
        (musteri_id, kod, expires_at),
    )
    conn.commit()
    cur.close()
    conn.close()


def verify_reset_code(musteri_id: int, kod: str) -> bool:
    _ensure_reset_table()
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id
        FROM sifre_sifirlama_kodlari
        WHERE musteri_id=%s AND kod=%s AND used=0 AND expires_at > NOW()
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (musteri_id, kod),
    )
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return False

    cur.execute("UPDATE sifre_sifirlama_kodlari SET used=1 WHERE id=%s", (row["id"],))
    conn.commit()
    cur.close()
    conn.close()
    return True
