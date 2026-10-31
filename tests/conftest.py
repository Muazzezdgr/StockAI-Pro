"""
Ortak test verileri.

Testler internete (Yahoo Finance) bağlanmaz. Bunun yerine tekrarlanabilir,
sahte (sentetik) fiyat serileri üretilir. Böylece testler her çalıştırmada
aynı sonucu verir ve ağ sorunlarından etkilenmez.
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sentetik_fiyat(n=300, seed=42, baslangic=100.0):
    """Rastgele yürüyüş (random walk) ile OHLCV verisi üretir."""
    rng = np.random.default_rng(seed)
    close = baslangic * np.exp(np.cumsum(rng.normal(0.0005, 0.02, n)))
    tarih = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame({
        "Open": close * (1 + rng.normal(0, 0.005, n)),
        "High": close * (1 + np.abs(rng.normal(0, 0.01, n))),
        "Low": close * (1 - np.abs(rng.normal(0, 0.01, n))),
        "Close": close,
        "Volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    }, index=tarih)


@pytest.fixture
def ham_veri():
    return sentetik_fiyat()


@pytest.fixture
def gostergeli_veri(ham_veri):
    from utils.data_utils import add_technical_indicators
    return add_technical_indicators(ham_veri.copy())
