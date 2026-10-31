# 📈 StockAI Pro — Stock, Crypto & BIST Analysis Platform

[![Tests](https://github.com/Muazzezdgr/StockAI-Pro/actions/workflows/tests.yml/badge.svg)](https://github.com/Muazzezdgr/StockAI-Pro/actions/workflows/tests.yml)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://stockai-pro.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)

An interactive decision-support dashboard for **US stocks, BIST 30 and major cryptocurrencies**. It combines 21 technical indicators with machine-learning direction forecasts (Random Forest / Gradient Boosting), backtesting, portfolio tracking and price alarms. It is built around one principle: **show the user how much to trust each number.**

🔗 **Live demo:** [stockai-pro.streamlit.app](https://stockai-pro.streamlit.app)

> 🧪 **QA focus:** 62 automated tests run on every push with GitHub Actions, without internet access, using synthetic price data. Testing uncovered **10 bugs**, including ML data leakage, a one-day misalignment in the backtest, and example news shown as real news. All are documented in the **[Bug Report](docs/BUG_REPORT.md)** and fixed.

<!-- Ekran görüntüsü: canlı uygulamadan alıp docs/screenshots/dashboard.png olarak ekleyin -->
<!-- ![Dashboard](docs/screenshots/dashboard.png) -->

---

## ✨ Features

| | |
|---|---|
| 🌍 **Multi-market** | NASDAQ/NYSE stocks, 30 BIST companies, 8 major cryptocurrencies; daily or hourly data |
| 🤖 **Direction forecast** | Random Forest / Gradient Boosting predict whether the next close will be higher, with a confidence score and feature importance |
| 📊 **21 technical indicators** | RSI, MACD, Bollinger Bands, Stochastic, ATR, OBV, moving averages, momentum, volatility… |
| 🚦 **Buy / Hold / Sell signal** | Rule-based score that combines RSI, MACD, Bollinger position and model confidence |
| 📈 **Backtest** | Strategy vs. Buy & Hold with stop-loss, win rate, max drawdown, annualized return and Sharpe ratio |
| 📰 **News sentiment** | NewsAPI headlines scored with a finance keyword lexicon (English + Turkish) |
| ⚖️ **Comparison** | Two symbols side by side |
| 💼 **Portfolio & alarms** | Track holdings and set price alerts |
| 📄 **PDF report** | Export the analysis as a shareable report |

### Transparency by design
- The **model confidence** explanation shows how the score is calculated and what it does *not* mean.
- The backtest warns when too few trades were made for the result to be statistically meaningful.
- Without a NewsAPI key, the app shows **clearly labeled example headlines** and never presents them as real news.
- The LSTM model is offered **only when TensorFlow is installed**. The cloud demo runs Random Forest and Gradient Boosting, and the interface says so.

---

## 🏗️ Project Structure

```
app.py                  Entry point: sidebar navigation, symbol selection
pages/                  One module per screen (dashboard, model_training, backtest, …)
utils/
├── data_utils.py       Data download (yfinance), 21 indicators, train/test preparation
├── model_utils.py      RF / GB training, evaluation, next-day prediction, optional LSTM
├── backtest_utils.py   Backtest simulation and metrics (pure functions, fully tested)
├── sentiment_utils.py  NewsAPI client + lexicon-based sentiment
├── pdf_report.py       PDF export (fpdf2)
└── chart_theme.py, ui.py   Shared chart style and UI components
tests/                  pytest suite (unit + Streamlit AppTest)
docs/
├── BUG_REPORT.md       Test findings: reproduction steps, root cause, fix
└── course-project/     Original course deliverables (notebook, report, slides)
```

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
pytest
```

| Area | What is verified |
|---|---|
| **Indicators** | All 21 features present, no NaN, RSI always 0–100, RSI → 100 / 0 for strictly rising / falling prices |
| **Boundary values** | Buy/sell signal at exactly the 2.5 threshold, market-cap formatting at 1M / 1B / 1T |
| **ML data integrity** | Scaler is fitted on training data only (no leakage); chronological split; next-day prediction uses the latest day |
| **Backtest** | Buy/sell rules, stop-loss, open position at period end, max drawdown, annualization, prediction ↔ price alignment |
| **Sentiment** | Whole-word matching, no double counting, Turkish word stems |
| **App smoke (Streamlit AppTest)** | All 8 pages render without exceptions; demo-news warning is shown; LSTM hidden without TensorFlow |

**Sanity check:** on a synthetic random-walk series the model scores ~51%. That is the expected result for unpredictable data, and a much higher score would indicate leakage.

---

## 🚀 Getting Started

**Windows (one click):** double-click `CALISTIR.bat`. The browser opens at `http://localhost:8501`.

**Manual:**
```bash
git clone https://github.com/Muazzezdgr/StockAI-Pro.git
cd StockAI-Pro
pip install -r requirements.txt
streamlit run app.py
```

**Optional:**
- **Real news:** get a free key at [newsapi.org](https://newsapi.org) and set `NEWSAPI_KEY` as an environment variable, or add it to `.streamlit/secrets.toml` (ignored by git).
- **LSTM:** `pip install tensorflow` locally; the LSTM option then appears on the Model Training page.

### Data source
Market data is downloaded live from Yahoo Finance via the [`yfinance`](https://pypi.org/project/yfinance/) library, so no dataset is stored in the repository.

---

## 📌 Known Limitations

- **Data licensing:** `yfinance` uses Yahoo Finance data intended for personal and educational use. A commercial product would need a licensed market-data provider.
- **Forecast quality:** next-day direction forecasts on liquid markets are typically close to 50% accuracy. The tool is for analysis and learning, not for trading decisions.
- **Session storage:** portfolio and alarms live in the browser session and reset when the session ends.
- **Sentiment:** lexicon-based keyword scoring, not a trained language model; it does not understand negation or context.

## ⚠️ Disclaimer

This application is for **educational and informational purposes only** and is **not investment advice**. Model outputs are statistical estimates based on past data and do not guarantee future price movements.

---

## 🛠️ Tech Stack

Python · Streamlit · scikit-learn · pandas · NumPy · Plotly · yfinance · fpdf2 · pytest · GitHub Actions · *(optional)* TensorFlow/Keras

## 🇹🇷 Türkçe Özet

**StockAI Pro**, ABD hisseleri, BIST 30 ve kripto paralar için teknik analiz ve makine öğrenmesi (Random Forest / Gradient Boosting) ile yön tahmini yapan bir karar destek panelidir. Backtest, portföy takibi, fiyat alarmı, haber duygu analizi ve PDF rapor içerir.

Proje **62 otomatik testle** doğrulanır. Test sürecinde **10 hata** bulunup düzeltilmiştir; aralarında makine öğrenmesinde veri sızıntısı, backtest'te bir günlük kayma ve örnek haberlerin gerçek haber gibi gösterilmesi de vardır. Ayrıntılar için: [Bug Report](docs/BUG_REPORT.md).

**Yatırım tavsiyesi değildir.**

---

*Started as a university course project (Yapay Zeka 2, Bilgisayar Programcılığı — Bergama MYO; original deliverables in [`docs/course-project`](docs/course-project)), then developed further by Muazzez Doğru: multi-market support, backtest metrics, portfolio, alarms, comparison, PDF export, UI redesign and the test suite.*

**Developer:** Muazzez Doğru · [GitHub](https://github.com/Muazzezdgr)
