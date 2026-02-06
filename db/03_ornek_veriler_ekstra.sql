-- ============================================================
-- EKSTRA ÖRNEK VERİLER
-- Daha fazla test verisi için
-- ============================================================

USE kuru_temizleme;

-- ============================================================
-- 1. EK MÜŞTERİLER
-- ============================================================
INSERT INTO musteriler (ad_soyad, email, telefon, adres, sifre, rol) VALUES
('Cem Yıldız', 'cem.yildiz@email.com', '05328889900', 'Ataşehir, İstanbul', 'sifre123', 'musteri'),
('Derya Acar', 'derya.acar@email.com', '05329990011', 'Yenimahalle, Ankara', 'sifre123', 'musteri'),
('Emre Bulut', 'emre.bulut@email.com', '05320011223', 'Bornova, İzmir', 'sifre123', 'musteri'),
('Gülay Yüksel', 'gulay.yuksel@email.com', '05321122334', 'Osmangazi, Bursa', 'sifre123', 'musteri'),
('Hakan Şen', 'hakan.sen@email.com', '05322233445', 'Kepez, Antalya', 'sifre123', 'musteri'),
('İpek Aydın', 'ipek.aydin@email.com', '05323344556', 'Beşiktaş, İstanbul', 'sifre123', 'musteri'),
('Kemal Özkan', 'kemal.ozkan@email.com', '05324455667', 'Mamak, Ankara', 'sifre123', 'musteri'),
('Leyla Çınar', 'leyla.cinar@email.com', '05325566778', 'Karşıyaka, İzmir', 'sifre123', 'musteri');

-- ============================================================
-- 2. EK ŞUBELER
-- ============================================================
INSERT INTO subeler (ad, sehir, adres, telefon, aktif) VALUES
('Ataşehir Şubesi', 'İstanbul', 'Barbaros Mahallesi, Ataşehir/İstanbul', '02161234568', 1),
('Yenimahalle Şubesi', 'Ankara', 'Yenimahalle Caddesi No:56, Yenimahalle/Ankara', '03121234568', 1),
('Bornova Şubesi', 'İzmir', 'Bornova Caddesi No:89, Bornova/İzmir', '02321234568', 1),
('Beşiktaş Şubesi', 'İstanbul', 'Beşiktaş Meydanı No:23, Beşiktaş/İstanbul', '02161234569', 1),
('Kadıköy 2. Şubesi', 'İstanbul', 'Moda Caddesi No:45, Kadıköy/İstanbul', '02161234570', 0); -- Pasif şube

-- ============================================================
-- 3. EK KURYE
-- ============================================================
INSERT INTO kuryeler (ad_soyad, telefon, email, sube_id, aktif) VALUES
('Recep Güneş', '05326666666', 'recep.gunes@akpak.com', 2, 1),
('Salih Yılmaz', '05327777777', 'salih.yilmaz@akpak.com', 3, 1),
('Tolga Kaya', '05328888888', 'tolga.kaya@akpak.com', 4, 1),
('Uğur Demir', '05329999999', 'ugur.demir@akpak.com', 5, 1),
('Veli Çelik', '05321010101', 'veli.celik@akpak.com', 6, 0); -- Pasif kurye

-- ============================================================
-- 4. EK SİPARİŞLER (Farklı durumlarda)
-- ============================================================
INSERT INTO siparisler (musteri_id, sube_id, kurye_id, siparis_tarihi, teslim_tarihi, durum, aciklama, odeme_yontemi) VALUES
(9, 1, 1, '2024-01-20 08:00:00', NULL, 'ALINDI', 
 'Şube: İstanbul - Kadıköy Şubesi\nAdres: Ataşehir, İstanbul\nÖdeme yöntemi: kapida\n1 x Takım Elbise (yikama_kurutma_utu) = 290 TL\nTahmini toplam tutar: 290 TL', 
 'kapida'),
(10, 2, 3, '2024-01-20 10:15:00', NULL, 'KURYE YOLDA', 
 'Şube: Ankara - Ankara Merkez\nAdres: Yenimahalle, Ankara\nÖdeme yöntemi: kart\n2 x Çorap (çift) (sadece_utu) = 120 TL\nTahmini toplam tutar: 120 TL', 
 'kart'),
(11, 3, 4, '2024-01-20 12:30:00', '2024-01-22 15:00:00', 'TESLIM EDILDI', 
 'Şube: İzmir - İzmir Alsancak\nAdres: Bornova, İzmir\nÖdeme yöntemi: kapida\nÇamaşır filesi adedi: 2 (300 TL/adet)\nTahmini toplam tutar: 600 TL', 
 'kapida'),
(12, 4, 5, '2024-01-21 09:45:00', NULL, 'HAZIRLANIYOR', 
 'Şube: Bursa - Bursa Nilüfer\nAdres: Osmangazi, Bursa\nÖdeme yöntemi: kapida\n1 x Gömlek (yikama) = 70 TL\n1 x Tişört / Crop (yikama) = 60 TL\n1 x Pantolon / Eşofman / Tayt (yikama_kurutma) = 110 TL\nTahmini toplam tutar: 240 TL', 
 'kapida'),
(13, 5, NULL, '2024-01-21 14:20:00', NULL, 'TESLIMAT ICIN KURYE YOLA CIKTI', 
 'Şube: Antalya - Antalya Konyaaltı\nAdres: Kepez, Antalya\nÖdeme yöntemi: kart\n1 x Elbise / Etek (yikama_kurutma_utu) = 170 TL\n1 x Kazak / Sweatshirt (yikama_kurutma) = 100 TL\nTahmini toplam tutar: 270 TL', 
 'kart'),
(14, 6, 1, '2024-01-22 11:00:00', NULL, 'ALINDI', 
 'Şube: İstanbul - Ataşehir Şubesi\nAdres: Beşiktaş, İstanbul\nÖdeme yöntemi: kapida\n1 x Mont / Kaban (yikama_kurutma) = 230 TL\nTahmini toplam tutar: 230 TL', 
 'kapida'),
(15, 2, 3, '2024-01-22 13:30:00', '2024-01-24 10:00:00', 'TESLIM EDILDI', 
 'Şube: Ankara - Yenimahalle Şubesi\nAdres: Mamak, Ankara\nÖdeme yöntemi: kart\n3 x Gömlek (yikama_kurutma_utu) = 300 TL\n2 x Pantolon / Eşofman / Tayt (yikama_kurutma) = 220 TL\nTahmini toplam tutar: 520 TL', 
 'kart'),
(16, 3, 4, '2024-01-23 15:45:00', NULL, 'HAZIRLANIYOR', 
 'Şube: İzmir - Bornova Şubesi\nAdres: Karşıyaka, İzmir\nÖdeme yöntemi: kapida\nÇamaşır filesi adedi: 1 (300 TL/adet)\n1 x Takım Elbise (yikama_kurutma_utu) = 290 TL\nTahmini toplam tutar: 590 TL', 
 'kapida');

-- ============================================================
-- 5. EK SİPARİŞ ÖĞELERİ
-- ============================================================
INSERT INTO siparis_ogeleri (siparis_id, hizmet_id, adet, birim_fiyat) VALUES
(6, NULL, 1, 290.00),  -- 1 takım elbise
(7, NULL, 1, 120.00),  -- 2 çorap sadece ütü
(8, NULL, 1, 600.00),  -- 2 file
(9, NULL, 1, 70.00),   -- 1 gömlek yıkama
(9, NULL, 1, 60.00),   -- 1 tişört yıkama
(9, NULL, 1, 110.00),  -- 1 pantolon yıkama+kurutma
(10, NULL, 1, 170.00), -- 1 elbise yıkama+kurutma+ütü
(10, NULL, 1, 100.00), -- 1 kazak yıkama+kurutma
(11, NULL, 1, 230.00), -- 1 mont yıkama+kurutma
(12, NULL, 1, 300.00), -- 3 gömlek yıkama+kurutma+ütü
(12, NULL, 1, 220.00), -- 2 pantolon yıkama+kurutma
(13, NULL, 1, 300.00), -- 1 file
(13, NULL, 1, 290.00); -- 1 takım elbise

-- ============================================================
-- 6. EK İLETİŞİM MESAJLARI
-- ============================================================
INSERT INTO iletisim_mesajlari (ad, email, mesaj, okundu) VALUES
('Nazlı Kılıç', 'nazli.kilic@email.com', 'Siparişimi iptal etmek istiyorum.', 0),
('Okan Yılmaz', 'okan.yilmaz@email.com', 'Kurye ne zaman gelecek?', 1),
('Pınar Aydın', 'pinar.aydin@email.com', 'Fiyatlarınız çok uygun, teşekkürler!', 1),
('Rıza Özdemir', 'riza.ozdemir@email.com', 'Şubelerinizde nakit ödeme kabul ediliyor mu?', 0),
('Seda Yücel', 'seda.yucel@email.com', 'Sipariş takip sisteminiz çok kullanışlı.', 1);
