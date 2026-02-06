-- ============================================================
-- ŞUBE VE PERSONEL VERİLERİ
-- Şubelere personel atamaları
-- ============================================================

USE kuru_temizleme;

-- ============================================================
-- 1. PERSONEL EKLEME (Şubelere göre)
-- ============================================================

-- İstanbul - Kadıköy Şubesi Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Ahmet Tekin', '05321000001', 'ahmet.tekin@akpak.com', 1, 'Müdür', 1),
('Ayşe Yıldız', '05321000002', 'ayse.yildiz@akpak.com', 1, 'Operatör', 1),
('Mehmet Çelik', '05321000003', 'mehmet.celik@akpak.com', 1, 'Operatör', 1),
('Fatma Özkan', '05321000004', 'fatma.ozkan@akpak.com', 1, 'Ütücü', 1);

-- Ankara - Ankara Merkez Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Ali Demir', '05321000005', 'ali.demir@akpak.com', 2, 'Müdür', 1),
('Zeynep Kaya', '05321000006', 'zeynep.kaya@akpak.com', 2, 'Operatör', 1),
('Mustafa Şahin', '05321000007', 'mustafa.sahin@akpak.com', 2, 'Operatör', 1),
('Elif Arslan', '05321000008', 'elif.arslan@akpak.com', 2, 'Ütücü', 1);

-- İzmir - İzmir Alsancak Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Cem Yılmaz', '05321000009', 'cem.yilmaz@akpak.com', 3, 'Müdür', 1),
('Derya Öztürk', '05321000010', 'derya.ozturk@akpak.com', 3, 'Operatör', 1),
('Emre Bulut', '05321000011', 'emre.bulut@akpak.com', 3, 'Operatör', 1),
('Gülay Yüksel', '05321000012', 'gulay.yuksel@akpak.com', 3, 'Ütücü', 1);

-- Bursa - Bursa Nilüfer Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Hakan Şen', '05321000013', 'hakan.sen@akpak.com', 4, 'Müdür', 1),
('İpek Aydın', '05321000014', 'ipek.aydin@akpak.com', 4, 'Operatör', 1),
('Kemal Özkan', '05321000015', 'kemal.ozkan@akpak.com', 4, 'Operatör', 1),
('Leyla Çınar', '05321000016', 'leyla.cinar@akpak.com', 4, 'Ütücü', 1);

-- Antalya - Antalya Konyaaltı Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Murat Yıldırım', '05321000017', 'murat.yildirim@akpak.com', 5, 'Müdür', 1),
('Nazlı Kılıç', '05321000018', 'nazli.kilic@akpak.com', 5, 'Operatör', 1),
('Okan Yılmaz', '05321000019', 'okan.yilmaz@akpak.com', 5, 'Operatör', 1),
('Pınar Aydın', '05321000020', 'pinar.aydin@akpak.com', 5, 'Ütücü', 1);

-- İstanbul - Ataşehir Şubesi Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Rıza Özdemir', '05321000021', 'riza.ozdemir@akpak.com', 6, 'Müdür', 1),
('Seda Yücel', '05321000022', 'seda.yucel@akpak.com', 6, 'Operatör', 1),
('Tolga Kaya', '05321000023', 'tolga.kaya@akpak.com', 6, 'Operatör', 1);

-- Ankara - Yenimahalle Şubesi Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Uğur Demir', '05321000024', 'ugur.demir@akpak.com', 7, 'Müdür', 1),
('Veli Çelik', '05321000025', 'veli.celik@akpak.com', 7, 'Operatör', 1),
('Yasin Yıldız', '05321000026', 'yasin.yildiz@akpak.com', 7, 'Operatör', 1);

-- İzmir - Bornova Şubesi Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Zeki Özkan', '05321000027', 'zeki.ozkan@akpak.com', 8, 'Müdür', 1),
('Aslı Şahin', '05321000028', 'asli.sahin@akpak.com', 8, 'Operatör', 1),
('Burak Kaya', '05321000029', 'burak.kaya@akpak.com', 8, 'Operatör', 1);

-- İstanbul - Beşiktaş Şubesi Personeli
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Can Arslan', '05321000030', 'can.arslan@akpak.com', 9, 'Müdür', 1),
('Deniz Yılmaz', '05321000031', 'deniz.yilmaz@akpak.com', 9, 'Operatör', 1),
('Ece Öztürk', '05321000032', 'ece.ozturk@akpak.com', 9, 'Operatör', 1);

-- Pasif personel örneği
INSERT INTO personel (ad_soyad, telefon, email, sube_id, pozisyon, aktif) VALUES
('Eski Personel', '05321000033', 'eski.personel@akpak.com', 1, 'Operatör', 0);

-- ============================================================
-- 2. İŞ ATAMALARI (Personel-Sipariş İlişkileri)
-- ============================================================

-- Sipariş 1 - Teslim edildi (Tamamlandı)
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi, tamamlanma_tarihi) VALUES
(1, 2, '2024-01-15 10:35:00', 1, '2024-01-15 14:00:00'),  -- Ayşe Yıldız (Operatör)
(1, 4, '2024-01-15 10:35:00', 1, '2024-01-15 14:00:00');  -- Fatma Özkan (Ütücü)

-- Sipariş 2 - Hazırlanıyor (Devam ediyor)
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi) VALUES
(2, 6, '2024-01-16 14:25:00', 0),  -- Zeynep Kaya (Operatör)
(2, 8, '2024-01-16 14:25:00', 0);  -- Elif Arslan (Ütücü)

-- Sipariş 3 - Kurye yolda (Tamamlandı, teslim için bekliyor)
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi, tamamlanma_tarihi) VALUES
(3, 10, '2024-01-17 09:20:00', 1, '2024-01-17 11:00:00');  -- Derya Öztürk (Operatör)

-- Sipariş 4 - Alındı (Yeni atama)
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi) VALUES
(4, 14, '2024-01-18 11:50:00', 0),  -- İpek Aydın (Operatör)
(4, 16, '2024-01-18 11:50:00', 0);  -- Leyla Çınar (Ütücü)

-- Sipariş 5 - Alındı (Henüz atanmadı - NULL olabilir veya atanabilir)
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi) VALUES
(5, 18, '2024-01-19 16:35:00', 0);  -- Nazlı Kılıç (Operatör)

-- Sipariş 6 - Alındı
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi) VALUES
(6, 2, '2024-01-20 08:05:00', 0),   -- Ayşe Yıldız (Operatör)
(6, 4, '2024-01-20 08:05:00', 0);   -- Fatma Özkan (Ütücü)

-- Sipariş 7 - Kurye yolda
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi, tamamlanma_tarihi) VALUES
(7, 6, '2024-01-20 10:20:00', 1, '2024-01-20 12:00:00'),  -- Zeynep Kaya (Operatör)
(7, 8, '2024-01-20 10:20:00', 1, '2024-01-20 12:00:00');  -- Elif Arslan (Ütücü)

-- Sipariş 8 - Teslim edildi
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi, tamamlanma_tarihi) VALUES
(8, 10, '2024-01-20 12:35:00', 1, '2024-01-20 15:00:00'),  -- Derya Öztürk (Operatör)
(8, 12, '2024-01-20 12:35:00', 1, '2024-01-20 15:00:00'); -- Gülay Yüksel (Ütücü)

-- Sipariş 9 - Hazırlanıyor
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi) VALUES
(9, 14, '2024-01-21 09:50:00', 0),  -- İpek Aydın (Operatör)
(9, 16, '2024-01-21 09:50:00', 0);  -- Leyla Çınar (Ütücü)

-- Sipariş 10 - Teslimat için kurye yola çıktı
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi, tamamlanma_tarihi) VALUES
(10, 18, '2024-01-21 14:25:00', 1, '2024-01-21 16:00:00'), -- Nazlı Kılıç (Operatör)
(10, 20, '2024-01-21 14:25:00', 1, '2024-01-21 16:00:00'); -- Pınar Aydın (Ütücü)

-- Sipariş 11 - Alındı
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi) VALUES
(11, 22, '2024-01-22 11:05:00', 0);  -- Seda Yücel (Operatör)

-- Sipariş 12 - Teslim edildi
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi, tamamlanma_tarihi) VALUES
(12, 6, '2024-01-22 13:35:00', 1, '2024-01-22 16:00:00'),  -- Zeynep Kaya (Operatör)
(12, 8, '2024-01-22 13:35:00', 1, '2024-01-22 16:00:00'); -- Elif Arslan (Ütücü)

-- Sipariş 13 - Hazırlanıyor
INSERT INTO is_atamalari (siparis_id, personel_id, atama_tarihi, tamamlandi) VALUES
(13, 10, '2024-01-23 15:50:00', 0),  -- Derya Öztürk (Operatör)
(13, 12, '2024-01-23 15:50:00', 0);  -- Gülay Yüksel (Ütücü)

-- ============================================================
-- 3. NOTLAR
-- ============================================================
-- Bu dosya şubelere personel atamalarını ve siparişlere iş atamalarını içerir.
-- Her şubede genellikle:
--   - 1 Müdür
--   - 2-3 Operatör (kuru temizleme makinesi operatörü)
--   - 1 Ütücü
-- bulunmaktadır.
--
-- İş atamaları, hangi personelin hangi siparişi işlediğini takip etmek için kullanılır.
-- Bir siparişe birden fazla personel atanabilir (örneğin operatör + ütücü)
