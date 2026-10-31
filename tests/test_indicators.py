"""Teknik göstergeler, hedef değişken ve yardımcı fonksiyonlar."""
import numpy as np
import pandas as pd
import pytest

from utils.data_utils import (FEATURES, add_technical_indicators, compute_rsi,
                              compute_signal, create_target, format_market_cap,
                              is_crypto_symbol)


def test_tum_model_ozellikleri_hesaplanir(gostergeli_veri):
    eksik = [f for f in FEATURES if f not in gostergeli_veri.columns]
    assert eksik == []


def test_gostergelerde_bos_deger_kalmaz(gostergeli_veri):
    assert not gostergeli_veri[FEATURES].isna().any().any()


def test_rsi_her_zaman_0_100_arasinda(gostergeli_veri):
    assert gostergeli_veri["RSI"].between(0, 100).all()


def test_surekli_yukselen_fiyatta_rsi_100e_yakin():
    rsi = compute_rsi(pd.Series(np.arange(1, 101, dtype=float)))
    assert rsi.iloc[-1] > 99


def test_surekli_dusen_fiyatta_rsi_0a_yakin():
    rsi = compute_rsi(pd.Series(np.arange(100, 0, -1, dtype=float)))
    assert rsi.iloc[-1] < 1


def test_hedef_ertesi_gunun_yonunu_gosterir():
    df = pd.DataFrame({"Close": [100.0, 102.0, 101.0, 101.05]})
    hedef = create_target(df, threshold=0.001)
    # 100→102 yukarı (1), 102→101 aşağı (0), 101→101.05 %0.05 < eşik (0)
    assert hedef.tolist()[:3] == [1, 0, 0]


@pytest.mark.parametrize("sembol, beklenen", [
    ("BTC-USD", True), ("eth-usd", True), ("SOL-USDT", True),
    ("AAPL", False), ("THYAO.IS", False), ("", False), (None, False),
])
def test_kripto_sembol_tanima(sembol, beklenen):
    assert is_crypto_symbol(sembol) is beklenen


@pytest.mark.parametrize("deger, beklenen", [
    (None, "—"), (999_999, "$999,999"), (1e6, "$1.00M"),
    (1e9, "$1.00B"), (1e12, "$1.00T"), (2.5e12, "$2.50T"),
])
def test_piyasa_degeri_bicimlendirme_sinirlari(deger, beklenen):
    assert format_market_cap(deger) == beklenen


# Sinyal kuralı: skor >= 2.5 → AL, skor <= -2.5 → SAT, arası → TUT
@pytest.mark.parametrize("rsi, macd, bb, prob, beklenen", [
    (25, 1, 0.1, 0.5, "AL"),     # 2 + 1 + 1 = 4
    (75, -1, 0.9, 0.5, "SAT"),   # -2 - 1 - 1 = -4
    (50, 0, 0.5, 0.5, "TUT"),    # 0
    (50, 1, 0.1, 0.625, "AL"),   # 1 + 1 + 0.5 = 2.5 → tam sınır
    (50, 1, 0.1, 0.6, "TUT"),    # 2.4 → sınırın hemen altı
])
def test_al_sat_sinyali_sinir_degerleri(rsi, macd, bb, prob, beklenen):
    sinyal, _ = compute_signal(rsi, macd, bb, prob)
    assert sinyal == beklenen
