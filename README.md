
# 🔐 SAP Security Parameter Analyzer

SAP sistemlerindeki profil parametrelerini **RSPARAM raporu** üzerinden otomatik çeken, güvenlik önerileriyle karşılaştıran ve detaylı analiz raporu üreten Python scripti.


## 🚀 Ne Yapar?

`Parametre_incelemesi.py` scripti aşağıdaki işlemleri gerçekleştirir:

- SAP GUI Scripting kullanarak **RSPARAM** raporundan profil parametrelerini çeker  
- Çekilen değerleri `Parametreler.xlsx` içindeki önerilen değerlerle karşılaştırır  
- Sonuca göre durumu belirler:

  - SAME  
  - LOW  
  - HIGH  
  - DIFFERENT  

- Duruma uygun güvenlik tavsiyesini Excel’den seçer  
- Tüm analizi `security_analysis_report.xlsx` dosyasına yazar  



## 📌 RSPARAM Nedir?

RSPARAM, SAP sistemlerinde **instance/system profil parametrelerini** listelemek için kullanılan teknik bir rapordur.

- Kernel ve sistem ayarlarını okur  
- Güvenlik hardening süreçlerinde kritik rol oynar  



## 🔄 Çalışma Akışı


SAP RSPARAM → Parametreleri Çek (Scripting)
↓
Parametreler.xlsx → Önerilen Değerlerle Karşılaştır
↓
Durum Belirle (LOW / HIGH / DIFFERENT / SAME)
↓
Parametreler.xlsx → İlgili Tavsiye Kolonunu Seç
↓
security_analysis_report.xlsx → Detaylı Rapor Yaz



## ⚙️ Kurulum


pip install -r requirements.txt


### Gereksinimler

* Windows OS
* SAP GUI (Scripting aktif olmalı)
* Python 3.x


## 🧠 Analiz Mantığı

Her parametre için akıllı karşılaştırma yapılır:

| Durum     | Açıklama          | Kullanılan Tavsiye |
| --------- | ----------------- | ------------------ |
| SAME      | Mevcut = Önerilen | ✅ Aynıysa          |
| LOW       | Mevcut < Önerilen | ⚠️ Düşükse         |
| HIGH      | Mevcut > Önerilen | ❌ Yüksekse         |
| DIFFERENT | String farklı     | ❌ Yüksek/Farklı    |


## ⚠️ Önemli Notlar

* SAP GUI Script ID’leri sistemden sisteme değişebilir
* Kendi ortamınız için **SAP GUI Recorder** kullanarak ID’leri çıkarmanız gerekir
* Test senaryoları `Parametre_Analiz_Kodu_Testleri.docx` dosyasında yer almaktadır
* `Parametre_incelemesi.py` toplam 4 senaryo ile doğrulanmıştır


## ✅ Test Edilenler

* 122 SAP profil parametresi
* 4 farklı karşılaştırma senaryosu
* Sayısal + string değer kontrolleri
* NOT_FOUND / ERROR durum yönetimi


## 🛡️ Amaç

SAP sistemlerinde güvenlik hardening sürecini otomatikleştirerek:

* Manuel kontrol yükünü azaltmak
* Yanlış konfigürasyonları hızlı tespit etmek
* Standartlara uygun raporlama üretmek




