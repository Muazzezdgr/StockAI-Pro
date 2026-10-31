"""Backtest simülasyonu: alım-satım kuralları, metrikler ve veri hizalaması."""
import numpy as np
import pytest

from utils.backtest_utils import fiyatlari_hizala, run_backtest
from utils.data_utils import prepare_rf_data


def test_hic_islem_yoksa_sermaye_sabit_kalir():
    sonuc = run_backtest([100, 110, 90, 120], [0.5, 0.5, 0.5, 0.5], initial=1000)
    assert sonuc["trades"] == 0
    assert sonuc["ret_m"] == 0
    assert sonuc["portfolio"] == [1000, 1000, 1000, 1000]


def test_buy_and_hold_getirisi_dogru_hesaplanir():
    sonuc = run_backtest([100, 150], [0.5, 0.5], initial=1000)
    assert sonuc["ret_bh"] == pytest.approx(50.0)


def test_al_ve_karla_sat():
    # Gün 0: güven %90 > %60 → AL (100'den). Gün 2: güven %10 < %40 → SAT (120'den)
    sonuc = run_backtest([100, 110, 120], [0.9, 0.5, 0.1], initial=1000, thresh_pct=60)
    assert sonuc["trades"] == 1 and sonuc["wins"] == 1
    assert sonuc["portfolio"][-1] == pytest.approx(1200)


def test_stop_loss_tetiklenir():
    # %5 stop-loss: 100'den alınıp 94'e düşünce satılmalı
    sonuc = run_backtest([100, 94, 200], [0.9, 0.5, 0.5], initial=1000, stoploss_pct=5)
    assert sonuc["trade_log"][0]["çıkış"] == 94
    assert sonuc["portfolio"][-1] == pytest.approx(940)


def test_donem_sonunda_acik_pozisyon_kazanma_oranina_dahil_edilir():
    """Hiç satış sinyali gelmezse pozisyon dönem sonunda kapatılmalı ve işlem olarak sayılmalı."""
    sonuc = run_backtest([100, 110, 130], [0.9, 0.9, 0.9], initial=1000)
    assert sonuc["trades"] == 1
    assert sonuc["wins"] == 1              # 100 → 130 kârlı
    assert sonuc["win_rate"] == 100
    assert len(sonuc["trade_log"]) == 1


def test_max_drawdown():
    # 1000 → 1200 → 900: zirveden düşüş %25
    sonuc = run_backtest([100, 120, 90], [0.9, 0.5, 0.5], initial=1000, stoploss_pct=50)
    assert sonuc["max_dd"] == pytest.approx(-25.0)


def test_yilliklandirma_periyot_sayisini_kullanir():
    """Saatlik veride bir yıl 252 değil, çok daha fazla periyottur."""
    fiyatlar = list(np.linspace(100, 110, 50))
    gunluk = run_backtest(fiyatlar, [0.9] * 50, periods_per_year=252)
    saatlik = run_backtest(fiyatlar, [0.9] * 50, periods_per_year=252 * 7)
    assert saatlik["ann_return"] > gunluk["ann_return"]


@pytest.mark.parametrize("n", [200, 201, 202, 203, 204, 205])
def test_tahminler_dogru_gunun_fiyatiyla_eslesir(gostergeli_veri, n):
    """Her test tahmini, tahminin üretildiği günün kapanış fiyatıyla eşleşmeli (kaydırma olmamalı)."""
    df = gostergeli_veri.iloc[:n]
    _, X_test, _, _, scaler, kolonlar = prepare_rf_data(df)
    gercek_kapanis = scaler.inverse_transform(X_test)[:, kolonlar.index("Close")]
    fiyatlar = fiyatlari_hizala(df, len(X_test))
    np.testing.assert_allclose(fiyatlar, gercek_kapanis, rtol=1e-9)
