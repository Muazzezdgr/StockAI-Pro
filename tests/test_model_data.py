"""
Model veri hazırlığı — özellikle VERİ SIZINTISI (data leakage) kontrolü.

Veri sızıntısı: Test verisine ait bilginin eğitim sürecine karışması.
Model, sınavdan önce soruların bir kısmını görmüş öğrenci gibi olur;
doğruluk oranı gerçekte olduğundan yüksek görünür.
"""
import numpy as np

from utils.data_utils import FEATURES, prepare_lstm_data, prepare_rf_data


def test_rf_train_test_bolumu_zaman_sirasini_korur(gostergeli_veri):
    X_train, X_test, y_train, y_test, _, _ = prepare_rf_data(gostergeli_veri)
    beklenen_toplam = len(gostergeli_veri) - 1  # son günün hedefi bilinmez
    assert len(X_train) + len(X_test) == beklenen_toplam
    assert len(X_test) == beklenen_toplam - int(beklenen_toplam * 0.8)


def test_rf_scaler_sadece_egitim_verisiyle_fit_edilir(gostergeli_veri):
    """Ölçekleyici (scaler) test verisini GÖRMEMELİ."""
    X_train, _, _, _, scaler, _ = prepare_rf_data(gostergeli_veri)
    egitim_satirlari = gostergeli_veri[FEATURES].iloc[:len(X_train)]
    np.testing.assert_allclose(scaler.mean_, egitim_satirlari.mean().values, rtol=1e-9)


def test_lstm_scaler_sadece_egitim_verisiyle_fit_edilir(gostergeli_veri):
    window = 20
    X_train, X_test, _, _, scaler = prepare_lstm_data(gostergeli_veri, window=window)
    # Eğitim pencerelerinin kapsadığı son satır: (len(X_train) - 1) + window - 1
    son_egitim_satiri = len(X_train) + window - 1
    egitim = gostergeli_veri[FEATURES].iloc[:son_egitim_satiri]
    np.testing.assert_allclose(scaler.data_max_, egitim.max().values, rtol=1e-9)


def test_lstm_pencere_boyutlari(gostergeli_veri):
    X_train, X_test, y_train, y_test, _ = prepare_lstm_data(gostergeli_veri, window=20)
    assert X_train.shape[1:] == (20, len(FEATURES))
    assert len(X_train) == len(y_train) and len(X_test) == len(y_test)


def test_lstm_yetersiz_veride_cokmez(gostergeli_veri):
    X_train, X_test, y_train, y_test, _ = prepare_lstm_data(gostergeli_veri.iloc[:10], window=20)
    assert len(X_train) == 0 and len(X_test) == 0


def test_yarin_tahmini_son_gunun_verisini_kullanir(gostergeli_veri):
    """
    Tahmin, en son günün göstergelerine dayanmalı. Son günü değiştirince tahmin de
    değişmeli; eski kod son günü hiç kullanmadığı için tahmin aynı kalıyordu (BUG-06).
    """
    from utils.data_utils import FEATURES
    from utils.model_utils import yarin_icin_tahmin

    normal = yarin_icin_tahmin(gostergeli_veri)

    degisik = gostergeli_veri.copy()
    # Son günü, verideki en "düşüşçü" günün göstergeleriyle değiştir
    en_dusuk_rsi_gunu = degisik["RSI"].idxmin()
    degisik.loc[degisik.index[-1], FEATURES] = degisik.loc[en_dusuk_rsi_gunu, FEATURES].values

    assert 0.0 <= normal <= 1.0
    assert yarin_icin_tahmin(degisik) != normal
