"""
utils/data_utils.py
Veri çekme, teknik göstergeler, ön işleme.
"""
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


def is_crypto_symbol(symbol: str) -> bool:
    """Kripto para sembolü mü? (yfinance formatı: BTC-USD, ETH-USD, vb.)"""
    if not symbol or not isinstance(symbol, str):
        return False
    symbol = symbol.strip().upper()
    return symbol.endswith("-USD") or symbol.endswith("-USDT") or symbol.endswith("-BTC")


# ─── Veri Çekme ─────────────────────────────────────────────────────────────

def fetch_stock_data(symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """yfinance ile hisse/kripto verisi çek ve teknik göstergeleri hesapla."""
    try:
        effective_interval = interval if interval in {"1d", "1h"} else "1d"
        effective_period = period
        if effective_interval == "1h":
            effective_period = "2y"

        ticker = yf.Ticker(symbol)
        df = ticker.history(period=effective_period, interval=effective_interval, auto_adjust=True)
        if df.empty:
            return pd.DataFrame()
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.dropna(inplace=True)
        df = add_technical_indicators(df)
        return df
    except Exception as e:
        print(f"Veri çekme hatası ({symbol}): {e}")
        return pd.DataFrame()


def get_ticker_info(symbol: str) -> dict:
    """Hisse/kripto temel bilgileri."""
    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
        clean_name = symbol.replace(".IS", "").replace(".F", "")
        if is_crypto_symbol(symbol):
            clean_name = clean_name.replace("-USD", "").replace("-USDT", "")
            sector = "Kripto Para"
            industry = "Dijital Varlık"
        else:
            sector = info.get("sector", "—")
            industry = info.get("industry", "—")
        return {
            "name": info.get("longName", clean_name),
            "sector": sector,
            "industry": industry,
            "market_cap": info.get("marketCap", None),
            "pe_ratio": info.get("trailingPE", None),
            "52w_high": info.get("fiftyTwoWeekHigh", None),
            "52w_low":  info.get("fiftyTwoWeekLow", None),
            "currency": info.get("currency", "USD"),
        }
    except:
        return {"name": symbol, "sector": "—", "industry": "—"}


# ─── Teknik Göstergeler ──────────────────────────────────────────────────────

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    c = df["Close"].copy()
    h = df["High"].copy()
    l = df["Low"].copy()
    v = df["Volume"].copy()

    # Moving Averages
    df["MA10"]  = c.rolling(10).mean()
    df["MA20"]  = c.rolling(20).mean()
    df["MA50"]  = c.rolling(50).mean()
    df["EMA10"] = c.ewm(span=10, adjust=False).mean()
    df["EMA20"] = c.ewm(span=20, adjust=False).mean()

    # RSI
    df["RSI"] = compute_rsi(c, 14)

    # MACD
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["MACD"]        = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]   = df["MACD"] - df["MACD_Signal"]

    # Bollinger Bands
    sma20 = c.rolling(20).mean()
    std20 = c.rolling(20).std()
    df["BB_Upper"] = sma20 + 2 * std20
    df["BB_Lower"] = sma20 - 2 * std20
    df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / sma20
    df["BB_Pos"]   = (c - df["BB_Lower"]) / (df["BB_Upper"] - df["BB_Lower"] + 1e-9)

    # Stochastic Oscillator
    low14  = l.rolling(14).min()
    high14 = h.rolling(14).max()
    df["Stoch_K"] = 100 * (c - low14) / (high14 - low14 + 1e-9)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()

    # ATR (Average True Range)
    tr = pd.concat([
        h - l,
        (h - c.shift()).abs(),
        (l - c.shift()).abs()
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    # OBV (On Balance Volume)
    obv = [0]
    for i in range(1, len(df)):
        if c.iloc[i] > c.iloc[i-1]:
            obv.append(obv[-1] + v.iloc[i])
        elif c.iloc[i] < c.iloc[i-1]:
            obv.append(obv[-1] - v.iloc[i])
        else:
            obv.append(obv[-1])
    df["OBV"] = obv

    # Diğer türetilmiş özellikler
    df["Return"]      = c.pct_change()
    df["Volatility"]  = df["Return"].rolling(10).std()
    df["Momentum"]    = c - c.shift(10)
    df["Price_vs_MA"] = c / df["MA20"] - 1
    df["Trend"]       = (c > df["MA50"]).astype(int)
    df["Volume_MA"]   = v.rolling(20).mean()
    df["Volume_Ratio"] = v / (df["Volume_MA"] + 1e-9)

    df.dropna(inplace=True)
    return df


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs  = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi


# ─── Hedef Değişken ──────────────────────────────────────────────────────────

def create_target(df: pd.DataFrame, threshold: float = 0.001) -> pd.Series:
    """
    Ertesi gün fiyat yönü: 1 = yukarı, 0 = aşağı/yatay
    threshold: minimum % değişim (gürültüyü azaltır)
    """
    future_return = df["Close"].shift(-1) / df["Close"] - 1
    return (future_return > threshold).astype(int)


# ─── LSTM Veri Hazırlama ─────────────────────────────────────────────────────

FEATURES = [
    "Close", "MA10", "MA20", "MA50", "EMA10", "EMA20",
    "RSI", "MACD", "MACD_Signal", "MACD_Hist",
    "BB_Width", "BB_Pos", "Stoch_K", "Stoch_D",
    "ATR", "Return", "Volatility", "Momentum",
    "Price_vs_MA", "Trend", "Volume_Ratio"
]


def prepare_lstm_data(df: pd.DataFrame, window: int = 30, test_ratio: float = 0.2):
    """Sliding window ile LSTM giriş verisi oluştur."""
    from sklearn.preprocessing import MinMaxScaler

    target = create_target(df)
    feat_df = df[FEATURES].copy()

    # Son satırı çıkar (shift(-1) nedeniyle NaN hedef)
    feat_df = feat_df.iloc[:-1]
    target  = target.iloc[:-1]

    if len(feat_df) <= window:
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(feat_df)
        return np.empty((0, window, scaled.shape[1])), np.empty((0, window, scaled.shape[1])), np.array([]), np.array([]), scaler

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(feat_df)

    X, y = [], []
    for i in range(window, len(scaled)):
        X.append(scaled[i - window:i])
        y.append(target.iloc[i])

    X, y = np.array(X), np.array(y)
    if len(X) == 0:
        return np.empty((0, window, scaled.shape[1])), np.empty((0, window, scaled.shape[1])), np.array([]), np.array([]), scaler
    split = int(len(X) * (1 - test_ratio))
    return X[:split], X[split:], y[:split], y[split:], scaler


def prepare_rf_data(df: pd.DataFrame, test_ratio: float = 0.2):
    """Random Forest için düz feature matrisi."""
    from sklearn.preprocessing import StandardScaler

    target = create_target(df)
    feat_df = df[FEATURES].copy().iloc[:-1]
    target  = target.iloc[:-1]

    scaler = StandardScaler()
    X = scaler.fit_transform(feat_df)
    y = target.values

    split = int(len(X) * (1 - test_ratio))
    return X[:split], X[split:], y[:split], y[split:], scaler, feat_df.columns.tolist()


# ─── Yardımcı ────────────────────────────────────────────────────────────────

def format_market_cap(val):
    if val is None:
        return "—"
    if val >= 1e12:
        return f"${val/1e12:.2f}T"
    if val >= 1e9:
        return f"${val/1e9:.2f}B"
    if val >= 1e6:
        return f"${val/1e6:.2f}M"
    return f"${val:,.0f}"


def compute_signal(rsi, macd_hist, bb_pos, pred_prob):
    """Basit kural + model skoru ile alım/satım sinyali üret."""
    score = 0
    if rsi < 30:        score += 2
    elif rsi > 70:      score -= 2
    if macd_hist > 0:   score += 1
    elif macd_hist < 0: score -= 1
    if bb_pos < 0.2:    score += 1
    elif bb_pos > 0.8:  score -= 1
    score += (pred_prob - 0.5) * 4

    if score >= 2.5:  return "AL",  "badge-buy"
    if score <= -2.5: return "SAT", "badge-sell"
    return "TUT", "badge-hold"
