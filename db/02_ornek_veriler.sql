-- ============================================================
-- ÖRNEK VERİLER - TEMEL VERİLER
-- ============================================================

USE kuru_temizleme;

-- ============================================================
-- 1. MÜŞTERİLER (Örnek Müşteriler)
-- ============================================================
INSERT INTO musteriler (ad_soyad, email, telefon, adres, sifre, rol) VALUES
('Ahmet Yılmaz', 'ahmet.yilmaz@email.com', '05321234567', 'Kadıköy, İstanbul', 'sifre123', 'musteri'),
('Ayşe Demir', 'ayse.demir@email.com', '05329876543', 'Çankaya, Ankara', 'sifre123', 'musteri'),
('Mehmet Kaya', 'mehmet.kaya@email.com', '05321112233', 'Konak, İzmir', 'sifre123', 'musteri'),
('Fatma Şahin', 'fatma.sahin@email.com', '05324445566', 'Nilüfer, Bursa', 'sifre123', 'musteri'),
('Ali Öztürk', 'ali.ozturk@email.com', '05327778899', 'Muratpaşa, Antalya', 'sifre123', 'musteri'),
('Zeynep Arslan', 'zeynep.arslan@email.com', '05325556677', 'Ortahisar, Trabzon', 'sifre123', 'musteri'),
('Mustafa Çelik', 'mustafa.celik@email.com', '05323334455', 'Merkez, Kocaeli', 'sifre123', 'musteri'),
('Elif Yıldız', 'elif.yildiz@email.com', '05326667788', 'İskenderun, Hatay', 'sifre123', 'musteri');

-- Admin kullanıcı
INSERT INTO musteriler (ad_soyad, email, telefon, adres, sifre, rol) VALUES
('admin', 'admin@gmail.com', '05320000000', 'İstanbul', 'admin123', 'admin');

-- ============================================================
-- 2. ŞUBELER (Örnek Şubeler)
-- ============================================================
INSERT INTO subeler (ad, sehir, adres, telefon, aktif) VALUES
('Kadıköy Şubesi', 'İstanbul', 'Bağdat Caddesi No:123, Kadıköy/İstanbul', '02161234567', 1),
('Ankara Merkez', 'Ankara', 'Kızılay, Atatürk Bulvarı No:45, Çankaya/Ankara', '03121234567', 1),
('İzmir Alsancak', 'İzmir', 'Alsancak, Kordon Boyu No:78, Konak/İzmir', '02321234567', 1),
('Bursa Nilüfer', 'Bursa', 'Nilüfer Caddesi No:12, Nilüfer/Bursa', '02241234567', 1),
('Antalya Konyaaltı', 'Antalya', 'Konyaaltı Sahil Yolu No:34, Muratpaşa/Antalya', '02421234567', 1);

-- ============================================================
-- 3. KURYE (Örnek Kuryeler)
-- ============================================================
INSERT INTO kuryeler (ad_soyad, telefon, email, sube_id, aktif) VALUES
('Hasan Yıldırım', '05321111111', 'hasan.yildirim@akpak.com', 1, 1),
('Osman Doğan', '05322222222', 'osman.dogan@akpak.com', 1, 1),
('İbrahim Kılıç', '05323333333', 'ibrahim.kilic@akpak.com', 2, 1),
('Yusuf Aydın', '05324444444', 'yusuf.aydin@akpak.com', 3, 1),
('Murat Özdemir', '05325555555', 'murat.ozdemir@akpak.com', 4, 1);

-- ============================================================
-- 4. HİZMETLER (Örnek Hizmetler)
-- ============================================================
INSERT INTO hizmetler (hizmet_adi, aciklama, aktif) VALUES
('Kuru Temizleme', 'Profesyonel kuru temizleme hizmeti', 1),
('Yıkama', 'Standart yıkama hizmeti', 1),
('Yıkama + Kurutma', 'Yıkama ve kurutma hizmeti', 1),
('Yıkama + Kurutma + Ütü', 'Tam hizmet paketi', 1),
('Sadece Ütü', 'Sadece ütüleme hizmeti', 1);

-- ============================================================
-- 5. FİYAT AYARLARI (Varsayılan Fiyatlar)
-- ============================================================
-- Ürün baz fiyatları
INSERT INTO fiyat_ayarlari (tur, anahtar, deger) VALUES
('urun', 'gomlek', 70.00),
('urun', 'tisort', 60.00),
('urun', 'kazak', 90.00),
('urun', 'pantolon', 100.00),
('urun', 'elbise', 140.00),
('urun', 'mont', 220.00),
('urun', 'takim', 260.00),
('urun', 'corap', 20.00);

-- Hizmet ek ücretleri
INSERT INTO fiyat_ayarlari (tur, anahtar, deger) VALUES
('hizmet', 'yok', 0.00),
('hizmet', 'yikama', 0.00),
('hizmet', 'yikama_kurutma', 10.00),
('hizmet', 'yikama_kurutma_utu', 30.00),
('hizmet', 'sadece_utu', 40.00);

-- File fiyatı
INSERT INTO fiyat_ayarlari (tur, anahtar, deger) VALUES
('file', 'file', 300.00);

-- ============================================================
-- 6. SİPARİŞLER (Örnek Siparişler)
-- ============================================================
INSERT INTO siparisler (musteri_id, sube_id, kurye_id, siparis_tarihi, durum, aciklama, odeme_yontemi) VALUES
(1, 1, 1, '2024-01-15 10:30:00', 'TESLIM EDILDI', 
 'Şube: İstanbul - Kadıköy Şubesi\nAdres: Kadıköy, İstanbul\nÖdeme yöntemi: kapida\n2 x Gömlek (yikama_kurutma_utu) = 200 TL\nTahmini toplam tutar: 200 TL', 
 'kapida'),
(2, 2, 3, '2024-01-16 14:20:00', 'HAZIRLANIYOR', 
 'Şube: Ankara - Ankara Merkez\nAdres: Çankaya, Ankara\nÖdeme yöntemi: kart\n1 x Pantolon (yikama_kurutma) = 110 TL\n1 x Elbise (yikama_kurutma_utu) = 170 TL\nTahmini toplam tutar: 280 TL', 
 'kart'),
(3, 3, 4, '2024-01-17 09:15:00', 'KURYE YOLDA', 
 'Şube: İzmir - İzmir Alsancak\nAdres: Konak, İzmir\nÖdeme yöntemi: kapida\nÇamaşır filesi adedi: 1 (300 TL/adet)\nTahmini toplam tutar: 300 TL', 
 'kapida'),
(4, 4, 5, '2024-01-18 11:45:00', 'ALINDI', 
 'Şube: Bursa - Bursa Nilüfer\nAdres: Nilüfer, Bursa\nÖdeme yöntemi: kapida\n3 x Tişört / Crop (yikama) = 180 TL\n2 x Kazak / Sweatshirt (yikama_kurutma) = 200 TL\nTahmini toplam tutar: 380 TL', 
 'kapida'),
(5, 5, NULL, '2024-01-19 16:30:00', 'ALINDI', 
 'Şube: Antalya - Antalya Konyaaltı\nAdres: Muratpaşa, Antalya\nÖdeme yöntemi: kart\n1 x Mont / Kaban (yikama_kurutma_utu) = 250 TL\nTahmini toplam tutar: 250 TL', 
 'kart');

-- ============================================================
-- 7. SİPARİŞ ÖĞELERİ (Örnek Sipariş Öğeleri)
-- ============================================================
INSERT INTO siparis_ogeleri (siparis_id, hizmet_id, adet, birim_fiyat) VALUES
(1, NULL, 1, 200.00),  -- 2 gömlek yıkama+kurutma+ütü = 200 TL
(2, NULL, 1, 110.00),  -- 1 pantolon yıkama+kurutma = 110 TL
(2, NULL, 1, 170.00),  -- 1 elbise yıkama+kurutma+ütü = 170 TL
(3, NULL, 1, 300.00),  -- 1 file = 300 TL
(4, NULL, 1, 180.00),  -- 3 tişört yıkama = 180 TL
(4, NULL, 1, 200.00),  -- 2 kazak yıkama+kurutma = 200 TL
(5, NULL, 1, 250.00);  -- 1 mont yıkama+kurutma+ütü = 250 TL

-- ============================================================
-- 8. İLETİŞİM MESAJLARI (Örnek Mesajlar)
-- ============================================================
INSERT INTO iletisim_mesajlari (ad, email, mesaj, okundu) VALUES
('Can Özkan', 'can.ozkan@email.com', 'Merhaba, siparişlerim ne zaman hazır olacak?', 1),
('Selin Avcı', 'selin.avci@email.com', 'Fiyatlarınız hakkında bilgi almak istiyorum.', 0),
('Burak Koç', 'burak.koc@email.com', 'Şubeleriniz hangi saatler arası açık?', 1);
