@echo off
echo ================================================
echo   StockAI Pro - VS Code Kurulum Scripti
echo ================================================
echo.

REM Sanal ortam var mi kontrol et
if not exist ".venv" (
    echo [1/3] Sanal ortam olusturuluyor...
    python -m venv .venv
) else (
    echo [1/3] Sanal ortam zaten mevcut.
)

echo.
echo [2/3] Sanal ortam aktive ediliyor...
call .venv\Scripts\activate.bat

echo.
echo [3/3] Kutuphaneler yukleniyor...
python -m pip install --upgrade pip --quiet
pip install numpy pandas yfinance scikit-learn tensorflow plotly streamlit requests joblib matplotlib --quiet

echo.
echo ================================================
echo   KURULUM TAMAMLANDI!
echo ================================================
echo.
echo Simdi VS Code'da:
echo   1. Ctrl+Shift+P - "Python: Select Interpreter"
echo   2. .venv\Scripts\python.exe sec
echo   3. Sarı uyarilar kaybolur
echo.
echo Uygulamayi baslatmak icin:
echo   streamlit run app.py
echo.
pause
