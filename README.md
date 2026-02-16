
# 🔐 SAP Security Parameter Analyzer

# Kodun Genel Özeti

Bu script, bir SAP sistemi üzerindeki güvenlik parametrelerini **otomatik olarak analiz etmek** için tasarlanmıştır.

Temel amacı:

- `parametreler.xlsx` dosyasında listelenen kritik güvenlik parametrelerini okumak  
- SAP sistemindeki mevcut değerleri çekmek  
- Önerilen değerlerle karşılaştırmak  
- Sonuçları `security_analysis_report.xlsx` adlı detaylı bir rapora dönüştürmek  

## 1. Başlatma ve Hazırlık

- Script ilk olarak `parametreler.xlsx` dosyasını okur ve hangi SAP parametrelerinin denetleneceğini belirler.
- Ardından kullanıcının bilgisayarındaki SAP Logon programını başlatır.
- Belirtilen SAP sistemine kullanıcı adı ve şifre ile otomatik bağlanır.


## 2. SAP'den Veri Çekme (`sap_connect_and_extract` fonksiyonu)

- SAP sistemine giriş yaptıktan sonra `SA38` işlem kodunu çalıştırır.
- `RSPARAM` raporunu açar (sistemdeki tüm parametreleri gösterir).

Her parametre için:

- Excel’den aldığı parametre adına göre arama yapar.
- Mevcut değerini okur.
- Sistem varsayılan değerini alır.
- Kullanıcı tarafından atanmış değeri kaydeder.
- Parametre bulunamazsa bunu raporlar.

Tüm parametreler işlendiğinde:

- Ham verileri liste haline getirir.
- SAP bağlantısını kapatır.


## 3. Güvenlik Analizi ve Karşılaştırma (`security_advice_engine` fonksiyonu)

Bu aşama script’in **beyni** olarak düşünülebilir.

- SAP’den gelen ham veriyi alır.
- Tekrar `parametreler.xlsx` dosyasını okur.
- Her parametre için:

  - Önerilen değeri
  - Uyulmadığında verilecek güvenlik tavsiyesini yükler.
  - Mevcut SAP değerlerini önerilen değerlerle karşılaştırır.

## 4. Değerlendirme Mantığı (`analyze_security_parameter` fonksiyonu)

Karşılaştırma şu şekilde yapılır:

### Sayısal Değerler

Örnek:

login/fails_to_user_lock = 3

- Mevcut değer önerilen değerden büyük mü?
- Küçük mü?
- Eşit mi?

### Metinsel Değerler

Örnek:

TRUE / FALSE

- Mevcut değer önerilenle aynı mı?

Sonuçlara göre durum belirlenir:

- `SAME` – Aynı
- `HIGH` – Yüksek
- `LOW` – Düşük
- `DIFFERENT` – Farklı


## 5. Raporlama

Son aşamada:

- Parametre adı
- Mevcut değer
- Önerilen değer
- Karşılaştırma sonucu
- Güvenlik tavsiyesi

bir araya getirilir.

Tüm bilgiler:

security_analysis_report.xlsx  dosyasına yazılır.

Bu dosya denetimin nihai çıktısıdır ve:

- Riskli parametreleri
- Yapılması gereken aksiyonları açık şekilde gösterir.

## ⚠️ Önemli Notlar

* SAP GUI Script ID’leri sistemden sisteme değişebilir
* Kendi ortamınız için **SAP GUI Recorder** kullanarak ID’leri çıkarmanız gerekir
* Test senaryoları `Parametre_Analiz_Kodu_Testleri.docx` dosyasında yer almaktadır
* `Parametre_incelemesi.py` toplam 4 senaryo ile doğrulanmıştır

## 🛡️ Amaç

SAP sistemlerinde güvenlik hardening sürecini otomatikleştirerek:

* Manuel kontrol yükünü azaltmak
* Yanlış konfigürasyonları hızlı tespit etmek
* Standartlara uygun raporlama üretmek




