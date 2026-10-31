"""
Uygulama açılış (smoke) testleri — Streamlit AppTest ile.

Gerçek tarayıcı açmadan uygulamayı çalıştırır ve her sayfanın hatasız
yüklendiğini kontrol eder. Yahoo Finance yerine sentetik veri kullanılır.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from tests.conftest import sentetik_fiyat

APP = str(Path(__file__).resolve().parent.parent / "app.py")

SAYFALAR = ["📊  Dashboard", "🤖  Model Eğitimi", "📰  Haber Analizi", "📈  Backtest",
            "Karsilastirma", "💼  Portföyüm", "⏰  Alarmlar", "Yasal Uyari"]


@pytest.fixture(autouse=True)
def internetsiz_veri(monkeypatch):
    import utils.data_utils as du
    from utils.data_utils import add_technical_indicators

    monkeypatch.setattr(du, "fetch_stock_data",
                        lambda symbol, period="2y", interval="1d": add_technical_indicators(sentetik_fiyat(500)))
    monkeypatch.setattr(du, "get_ticker_info",
                        lambda symbol: {"name": symbol, "sector": "Test", "industry": "Test", "currency": "USD"})
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)


def _calistir(sayfa=None, analiz=False):
    at = AppTest.from_file(APP, default_timeout=60)
    if sayfa:
        at.session_state["nav_page"] = sayfa
    if analiz:
        at.session_state["analysis_active"] = True
    return at.run()


@pytest.mark.parametrize("sayfa", SAYFALAR)
def test_her_sayfa_hatasiz_acilir(sayfa):
    at = _calistir(sayfa)
    assert not at.exception, f"{sayfa}: {at.exception}"


def test_dashboard_analiz_calisir_ve_demo_haber_uyarisi_gosterir():
    at = _calistir("📊  Dashboard", analiz=True)
    assert not at.exception
    uyarilar = " ".join(w.value for w in at.warning)
    assert "Örnek haberler" in uyarilar


def test_bulutta_lstm_secenegi_gosterilmez():
    from utils.model_utils import lstm_kullanilabilir
    if lstm_kullanilabilir():
        pytest.skip("Bu ortamda TensorFlow kurulu")
    at = _calistir("🤖  Model Eğitimi")
    secenekler = [s for s in at.selectbox if "Model" in s.label]
    assert secenekler and "LSTM (Derin Öğrenme)" not in secenekler[0].options
