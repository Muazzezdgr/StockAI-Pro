# 📈 StockAI Pro — Hisse Senedi Yön Tahmini


---

## 🚀 EN KOLAY ÇALIŞTIRMA (Windows)

### ✅ Tek Tıkla Başlat
1. Bu klasörü bilgisayarınıza çıkarın
2. **`CALISTIR.bat`** dosyasına **çift tıklayın**
3. Tarayıcı otomatik açılır → `http://localhost:8501`

> ⚠️ Python kurulu değilse: https://www.python.org/downloads/
> Python indirirken **"Add to PATH"** seçeneğini işaretleyin!

---

## 🔧 Manuel Çalıştırma (Terminal ile)

```bash
# 1. Kütüphaneleri kur
pip install -r requirements.txt

# 2. Uygulamayı başlat
python -m streamlit run app.py

# 3. Tarayıcıda aç
# http://localhost:8501
```

---

## 📓 Google Colab Notebook

`stock_prediction_pro.ipynb` dosyasını Colab'da çalıştırmak için:

1. https://colab.research.google.com adresine gidin
2. **Dosya → Not Defteri Yükle** → `stock_prediction_pro.ipynb` seçin
3. **Tümünü Çalıştır** (Ctrl+F9)

---

## 📁 Proje Yapısı

```
📦 90240000271_90240000221_90240000220_C5/
│
├── 🚀 CALISTIR.bat                  ← Çift tıkla, otomatik başlar!
├── 📄 README.md                     ← Bu dosya
├── 📋 veri_seti_linki.txt           ← Veri kaynağı bilgisi
│
├── 🐍 app.py                        ← Ana Streamlit uygulaması
├── 📓 stock_prediction_pro.ipynb    ← Google Colab notebook
├── 📋 requirements.txt              ← Gerekli kütüphaneler
│
├── 📊 StockAI_Pro_SUNUM.pptx        ← Sunum dosyası
├── 📄 StockAI_Pro_RAPOR.pdf         ← Teknik rapor (PDF)
│
├── 📁 pages/
│   ├── dashboard.py                 ← Ana dashboard
│   ├── model_training.py            ← Model eğitimi
│   ├── news_analysis.py             ← Haber duygu analizi
│   ├── backtest.py                  ← Strateji backtest
│   └── about.py                     ← Hakkında
│
└── 📁 utils/
    ├── data_utils.py                ← Veri + 21 teknik gösterge
    ├── model_utils.py               ← LSTM + Random Forest
    └── sentiment_utils.py           ← NLP haber analizi
```

---

## 🖥️ Uygulama Nasıl Kullanılır?

### Senaryo 1 — Hisse Analizi (Dashboard)
1. Sol panelden **ABD** veya **BIST** piyasası seçin
2. Hisse senedi seçin (AAPL, TSLA, THYAO.IS...)
3. **ANALİZİ BAŞLAT** butonuna tıklayın
4. Dashboard'da fiyat, RSI, MACD, model tahmini görüntülenir

### Senaryo 2 — Model Eğitimi
1. Sol menüden **Model Eğitimi** sayfasına gidin
2. Model seçin: Random Forest / LSTM / Gradient Boosting
3. **MODELİ EĞİT** butonuna tıklayın
4. ROC eğrisi, Confusion Matrix, Feature Importance görüntülenir

### Senaryo 3 — Backtest Simülasyonu
1. Sol menüden **Backtest** sayfasına gidin
2. Başlangıç sermayesi ve parametreleri ayarlayın
3. **BACKTEST ÇALIŞTIR** butonuna tıklayın
4. Model stratejisi vs Buy&Hold karşılaştırması görüntülenir

---

| # | Dosya | Açıklama |
|---|-------|----------|
| 1 | `stock_prediction_pro.ipynb` | Tüm kodlar (veri, model, sonuç) |
| 2 | `StockAI_Pro_RAPOR.pdf` | Teknik rapor |
| 3 | `StockAI_Pro_SUNUM.pptx` | Sunum (16 slayt) |
| 4 | `app.py` + `pages/` + `utils/` | Arayüz kaynak kodu |
| 5 | `veri_seti_linki.txt` | Veri seti linki (yfinance API) |

---

## ⚙️ Gereksinimler

- Python 3.9 veya üzeri
- İnternet bağlantısı (yfinance veri çeker)
- Tarayıcı (Chrome/Firefox/Edge)

---


