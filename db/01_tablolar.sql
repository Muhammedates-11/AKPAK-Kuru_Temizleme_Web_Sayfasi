
CREATE DATABASE IF NOT EXISTS kuru_temizleme
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_turkish_ci;

USE kuru_temizleme;
-- 1. MÜŞTERİLER TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS musteriler (
    musteri_id INT AUTO_INCREMENT PRIMARY KEY,
    ad_soyad VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    telefon VARCHAR(20) UNIQUE NOT NULL,
    adres TEXT,
    kayit_tarihi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sifre VARCHAR(255) NOT NULL,
    rol ENUM('musteri', 'admin') NOT NULL DEFAULT 'musteri',
    INDEX idx_email (email),
    INDEX idx_telefon (telefon)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 2. ŞUBELER TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS subeler (
    sube_id INT AUTO_INCREMENT PRIMARY KEY,
    ad VARCHAR(255) NOT NULL,
    sehir VARCHAR(100) NOT NULL,
    adres TEXT,
    telefon VARCHAR(20),
    aktif TINYINT(1) NOT NULL DEFAULT 1,
    olusturma_tarihi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sehir (sehir),
    INDEX idx_aktif (aktif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 3. KURYE TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS kuryeler (
    kurye_id INT AUTO_INCREMENT PRIMARY KEY,
    ad_soyad VARCHAR(255) NOT NULL,
    telefon VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    sube_id INT,
    aktif TINYINT(1) NOT NULL DEFAULT 1,
    olusturma_tarihi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sube_id) REFERENCES subeler(sube_id) ON DELETE SET NULL,
    INDEX idx_sube (sube_id),
    INDEX idx_aktif (aktif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 4. SİPARİŞLER TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS siparisler (
    siparis_id INT AUTO_INCREMENT PRIMARY KEY,
    musteri_id INT NOT NULL,
    sube_id INT,
    kurye_id INT,
    siparis_tarihi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    teslim_tarihi DATETIME,
    durum VARCHAR(50) NOT NULL DEFAULT 'ALINDI',
    aciklama TEXT,
    odeme_yontemi VARCHAR(50) NOT NULL DEFAULT 'kapida',
    FOREIGN KEY (musteri_id) REFERENCES musteriler(musteri_id) ON DELETE RESTRICT,
    FOREIGN KEY (sube_id) REFERENCES subeler(sube_id) ON DELETE SET NULL,
    FOREIGN KEY (kurye_id) REFERENCES kuryeler(kurye_id) ON DELETE SET NULL,
    INDEX idx_musteri (musteri_id),
    INDEX idx_sube (sube_id),
    INDEX idx_durum (durum),
    INDEX idx_tarih (siparis_tarihi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 5. SİPARİŞ ÖĞELERİ TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS siparis_ogeleri (
    oge_id INT AUTO_INCREMENT PRIMARY KEY,
    siparis_id INT NOT NULL,
    hizmet_id INT,
    adet INT NOT NULL DEFAULT 1,
    birim_fiyat DECIMAL(10,2) NOT NULL,
    toplam_fiyat DECIMAL(10,2) GENERATED ALWAYS AS (adet * birim_fiyat) STORED,
    FOREIGN KEY (siparis_id) REFERENCES siparisler(siparis_id) ON DELETE CASCADE,
    INDEX idx_siparis (siparis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 6. HİZMETLER TABLOSU (Opsiyonel - gelecekte kullanım için)
-- ============================================================
CREATE TABLE IF NOT EXISTS hizmetler (
    hizmet_id INT AUTO_INCREMENT PRIMARY KEY,
    hizmet_adi VARCHAR(255) NOT NULL,
    aciklama TEXT,
    aktif TINYINT(1) NOT NULL DEFAULT 1,
    olusturma_tarihi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 7. İLETİŞİM MESAJLARI TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS iletisim_mesajlari (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ad VARCHAR(255),
    email VARCHAR(255),
    mesaj TEXT NOT NULL,
    tarih DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    okundu TINYINT(1) NOT NULL DEFAULT 0,
    INDEX idx_tarih (tarih),
    INDEX idx_okundu (okundu)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 8. FİYAT AYARLARI TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS fiyat_ayarlari (
    tur VARCHAR(20) NOT NULL,
    anahtar VARCHAR(64) NOT NULL,
    deger DECIMAL(10,2) NOT NULL,
    guncellendi TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (tur, anahtar)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 9. ŞİFRE SIFIRLAMA KODLARI TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS sifre_sifirlama_kodlari (
    id INT AUTO_INCREMENT PRIMARY KEY,
    musteri_id INT NOT NULL,
    kod VARCHAR(10) NOT NULL,
    expires_at DATETIME NOT NULL,
    used TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_musteri (musteri_id),
    INDEX idx_kod (kod),
    INDEX idx_expires (expires_at),
    FOREIGN KEY (musteri_id) REFERENCES musteriler(musteri_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 10. PERSONEL TABLOSU
-- ============================================================
CREATE TABLE IF NOT EXISTS personel (
    personel_id INT AUTO_INCREMENT PRIMARY KEY,
    ad_soyad VARCHAR(255) NOT NULL,
    telefon VARCHAR(20),
    email VARCHAR(255),
    sube_id INT,
    pozisyon VARCHAR(100),
    aktif TINYINT(1) NOT NULL DEFAULT 1,
    olusturma_tarihi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sube_id) REFERENCES subeler(sube_id) ON DELETE SET NULL,
    INDEX idx_sube (sube_id),
    INDEX idx_aktif (aktif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

-- ============================================================
-- 11. İŞ ATAMALARI TABLOSU (Personel-Sipariş İlişkisi)
-- ============================================================
CREATE TABLE IF NOT EXISTS is_atamalari (
    atama_id INT AUTO_INCREMENT PRIMARY KEY,
    siparis_id INT NOT NULL,
    personel_id INT NOT NULL,
    atama_tarihi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tamamlandi TINYINT(1) NOT NULL DEFAULT 0,
    tamamlanma_tarihi DATETIME,
    FOREIGN KEY (siparis_id) REFERENCES siparisler(siparis_id) ON DELETE CASCADE,
    FOREIGN KEY (personel_id) REFERENCES personel(personel_id) ON DELETE RESTRICT,
    INDEX idx_siparis (siparis_id),
    INDEX idx_personel (personel_id),
    INDEX idx_tamamlandi (tamamlandi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;


