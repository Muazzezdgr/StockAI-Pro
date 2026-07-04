# StockAI Pro

StockAI Pro, hisse senedi, kripto para ve BIST piyasalarını yapay zeka
modelleriyle analiz eden bir karar destek platformudur. LSTM ve Random
Forest tabanlı modellerle fiyat yönü tahmini yapar, haber duygu analizini
teknik göstergelerle birleştirir ve tüm tahminlerin arkasındaki güven
düzeyini şeffaf biçimde gösterir.

Streamlit üzerine kurulmuş olan uygulama, tek bir dosyayı çalıştırarak
tarayıcıda açılan interaktif bir dashboard sunar; kurulum veya sunucu
yönetimi gerektirmez.

## Özellikler

- **Çoklu piyasa desteği**: ABD hisseleri (NASDAQ/NYSE), BIST 30 şirketi ve
  başlıca kripto paralar (BTC, ETH, BNB, SOL ve diğerleri) tek arayüzden
  analiz edilir
- **AI destekli yön tahmini**: LSTM ve Random Forest modelleriyle fiyat
  yönü ve güven skoru üretilir
- **Haber duygu analizi**: İlgili sembole ait haberler NLP ile taranır ve
  pozitif/negatif/nötr olarak sınıflandırılır
- **Portföy takibi**: Sahip olunan varlıkları kaydedip güncel değer ve
  kâr/zarar durumunu anlık izleme
- **Fiyat alarmları**: Belirlenen seviyelere ulaşıldığında bildirim alma
- **Karşılaştırmalı analiz**: İki sembolü yan yana; fiyat, teknik gösterge
  ve model güveni açısından kıyaslama
- **PDF rapor dışa aktarma**: Analiz sonuçlarını paylaşılabilir bir rapora
  dönüştürme
- **Backtest simülasyonu**: Model stratejisini geçmiş veri üzerinde
  Buy & Hold ile karşılaştırma
- **Teknik gösterge kütüphanesi**: RSI, MACD ve benzeri 20'den fazla
  gösterge ile zenginleştirilmiş analiz

## Neden Farklı

**Şeffaflık önce gelir.** Model güven skoru kara kutu bir sayı değildir;
nasıl hesaplandığı ve neyi ifade ettiği kullanıcıya açıkça anlatılır.
Backtest sonuçları da az sayıda işlem üretildiğinde istatistiksel olarak
anlamlı olmayabileceği konusunda kullanıcıyı uyarır — sonuçlar abartılı bir
güvenle sunulmaz.

**Yerel piyasa desteği.** BIST 30 şirketleri uygulamaya özel olarak
tanımlanmıştır; Türkiye piyasasıyla ilgilenen kullanıcılar için ayrı bir
entegrasyon aranmasına gerek kalmaz.

**Açık geliştirme süreci.** Proje, geri bildirimlerle adım adım
şekillenen, geliştirmeye açık bir kaynak koddur.

## Kurulum

### Tek tıkla çalıştırma (Windows)

1. Proje klasörünü bilgisayarınıza indirin
2. `CALISTIR.bat` dosyasına çift tıklayın
3. Tarayıcı otomatik olarak `http://localhost:8501` adresinde açılır

Python kurulu değilse [python.org](https://www.python.org/downloads/)
adresinden indirin ve kurulum sırasında **"Add to PATH"** seçeneğini
işaretleyin.

### Manuel kurulum

```bash
# Gerekli kütüphaneleri kur
pip install -r requirements.txt

# Uygulamayı başlat
streamlit run app.py
```

Uygulama açıldıktan sonra `http://localhost:8501` adresinden erişilebilir.

## Kullanılan Teknolojiler

- **Python** — temel geliştirme dili
- **Streamlit** — interaktif web arayüzü
- **LSTM (derin öğrenme)** — zaman serisi fiyat tahmini
- **Random Forest** — sınıflandırma tabanlı yön tahmini
- **yfinance** — hisse, kripto ve BIST verisi
- **scikit-learn** — model eğitimi ve değerlendirme
- **Plotly** — interaktif grafikler
- **fpdf2** — PDF rapor oluşturma

## Ekran Görüntüsü

*(Uygulamanın bir ekran görüntüsünü buraya ekleyebilirsiniz.)*

## Yasal Uyarı

Bu uygulama yalnızca bilgilendirme ve eğitim amaçlıdır; yatırım tavsiyesi
niteliği taşımaz. Model tahminleri geçmiş verilere dayalı istatistiksel
çıkarımlardır ve gelecekteki fiyat hareketlerini garanti etmez. Yatırım
kararlarınızı vermeden önce bağımsız bir finansal danışmana başvurun.

## Lisans ve İletişim

Geliştirici: **Muazzez Doğru**

Sorularınız veya katkı önerileriniz için proje deposu üzerinden iletişime
geçebilirsiniz.
