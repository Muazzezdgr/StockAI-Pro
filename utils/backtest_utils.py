"""
utils/backtest_utils.py
Backtest simülasyonu — Streamlit'ten bağımsız, saf (pure) fonksiyonlar.
Sayfa (pages/backtest.py) sadece sonucu gösterir; hesaplama burada yapılır ve test edilir.
"""
import numpy as np

# Bir yıldaki periyot (mum) sayısı — getiri ve Sharpe yıllıklandırması için.
PERIYOT_YIL = {
    ("1d", False): 252,        # hisse: yılda ~252 işlem günü
    ("1d", True): 365,         # kripto: 7/24 işlem
    ("1h", False): 252 * 7,    # hisse: günde ~7 saatlik mum
    ("1h", True): 365 * 24,    # kripto: günde 24 saatlik mum
}


def periods_per_year(interval: str = "1d", crypto: bool = False) -> int:
    return PERIYOT_YIL.get((interval, crypto), 252)


def fiyatlari_hizala(df, n_probs, test_ratio=0.2):
    """
    Modelin test tahminlerine karşılık gelen kapanış fiyatlarını döndürür.

    prepare_rf_data son satırı (hedefi bilinmeyen gün) atıp kalan len(df)-1 satırı
    böler. Fiyatlar da AYNI noktadan bölünmeli; aksi halde tahmin ile fiyat
    bir gün kayar (BUG-02).
    """
    split = int((len(df) - 1) * (1 - test_ratio))
    n = min(n_probs, len(df) - 1 - split)
    return df["Close"].iloc[split:split + n].values


def run_backtest(prices, probs, initial=10000.0, thresh_pct=60, stoploss_pct=5,
                 periods_per_year=252):
    """
    Kural: model güveni > eşik ise AL; güven < (1 - eşik) veya zarar > stop-loss ise SAT.
    Dönem sonunda açık pozisyon son fiyattan kapatılır ve işlem olarak kaydedilir.
    """
    capital = float(initial)
    position = 0.0
    portfolio = []
    buy_hold = [float(initial) / prices[0] * p for p in prices]
    trades = wins = 0
    entry_price = 0.0
    trade_log = []

    def pozisyonu_kapat(gun, fiyat):
        nonlocal capital, position, wins
        capital = position * fiyat
        kazandi = fiyat > entry_price
        wins += int(kazandi)
        trade_log.append({"gün": gun, "giriş": entry_price, "çıkış": fiyat,
                          "kar": (fiyat - entry_price) / entry_price * 100,
                          "sonuç": "✅ Kar" if kazandi else "❌ Zarar"})
        position = 0.0

    for i, (price, prob) in enumerate(zip(prices, probs)):
        if prob > thresh_pct / 100 and position == 0:
            position = capital / price
            capital = 0.0
            entry_price = price
            trades += 1
        elif position > 0:
            loss_pct = (price - entry_price) / entry_price * 100
            if prob < (1 - thresh_pct / 100) or loss_pct < -stoploss_pct:
                pozisyonu_kapat(i, price)
        portfolio.append(capital + position * price)

    # BUG-03: Açık kalan pozisyon önceden işlem sayısına dahil edilip kazanç
    # hesabına katılmıyordu → kazanma oranı olduğundan düşük görünüyordu.
    if position > 0:
        son = len(portfolio) - 1
        pozisyonu_kapat(son, prices[son])
        portfolio[-1] = capital

    arr = np.array(portfolio, dtype=float)
    final_m, final_bh = arr[-1], buy_hold[len(arr) - 1]

    # BUG-04: Yıllıklandırma her zaman 252 (günlük hisse) varsayıyordu.
    ann_return = None
    if initial > 0 and len(arr) > 0:
        ann_return = (final_m / initial) ** (periods_per_year / len(arr)) - 1.0

    sharpe = None
    if len(arr) > 2:
        getiriler = np.diff(arr) / arr[:-1]
        std = getiriler.std(ddof=1)
        if std > 0:
            sharpe = getiriler.mean() / std * np.sqrt(periods_per_year)

    peak = np.maximum.accumulate(arr)
    max_dd = float(((arr - peak) / peak * 100).min())

    return {
        "portfolio": arr.tolist(), "buy_hold": buy_hold, "trades": trades, "wins": wins,
        "trade_log": trade_log,
        "ret_m": (final_m - initial) / initial * 100,
        "ret_bh": (final_bh - initial) / initial * 100,
        "win_rate": (wins / trades * 100) if trades > 0 else 0,
        "ann_return": ann_return, "sharpe": sharpe, "max_dd": max_dd,
    }
