@echo off
chcp 65001 >nul
cls
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║         StockAI Pro — Otomatik Kurulum ve Başlatma      ║
echo  ║         Yapay Zeka 2 - C5 Final Projesi                 ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  HATA: Python bulunamadi!
    echo  Lutfen https://www.python.org/downloads/ adresinden
    echo  Python 3.10 veya uzeri yukleyin.
    echo.
    pause
    exit /b 1
)
python --version
echo  Python bulundu!

echo.
echo  [2/4] Gerekli kutuphaneler yukleniyor...
echo  (Bu islem 2-5 dakika surebilir, lutfen bekleyin)
echo.
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo  Hata olustu. Tekrar deneniyor...
    pip install streamlit yfinance pandas numpy scikit-learn plotly requests joblib matplotlib
)

echo.
echo  [3/4] Kurulum tamamlandi!
echo.
echo  [4/4] Uygulama baslatiliyor...
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║  Tarayici otomatik acilacak: http://localhost:8501      ║
echo  ║  Durdurmak icin bu pencereyi kapatin (Ctrl+C)           ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
python -m streamlit run app.py
pause
