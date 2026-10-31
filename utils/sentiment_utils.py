"""
utils/sentiment_utils.py
Haber duygu analizi — NewsAPI + finans odaklı sözlük (lexicon) skoru.

Not: Bu bir makine öğrenmesi NLP modeli değil, kural tabanlı bir sözlük
yöntemidir: başlıkta geçen olumlu/olumsuz finans kelimeleri sayılır.
NEWSAPI_KEY tanımlı değilse örnek (demo) haberler döner ve bu açıkça işaretlenir.
"""
import os
import re
from datetime import datetime, timedelta

import requests

# İngilizce kelimeler TAM kelime olarak eşleşir ("gain" ≠ "against").
POSITIVE_EN = {
    "growth", "profit", "profits", "gain", "gains", "surge", "surges", "rally", "rallies",
    "beat", "beats", "strong", "record", "high", "bullish", "upgrade", "upgrades", "buy",
    "outperform", "revenue", "increase", "rise", "rises", "positive", "recovery", "boost",
}
NEGATIVE_EN = {
    "loss", "losses", "decline", "declines", "fall", "falls", "drop", "drops", "crash",
    "weak", "miss", "misses", "downgrade", "downgrades", "sell", "underperform", "cut",
    "cuts", "risk", "risks", "concern", "concerns", "negative", "bearish", "deficit",
    "layoff", "layoffs", "lawsuit",
}
# Türkçe eklemeli bir dil olduğu için kelime KÖKÜ ile eşleşir ("kazanç" → "kazancı" da sayılır).
POSITIVE_TR = ["yükseliş", "kazan", "büyüme", "rekor", "güçlü", "artış"]
NEGATIVE_TR = ["düşüş", "kayıp", "kayb", "zayıf", "endişe", "azalış"]

# Geriye dönük uyumluluk için birleşik listeler
POSITIVE_WORDS = sorted(POSITIVE_EN) + POSITIVE_TR
NEGATIVE_WORDS = sorted(NEGATIVE_EN) + NEGATIVE_TR

_KELIME = re.compile(r"[a-zçğıöşü]+")


def _kucuk_harf(metin: str) -> str:
    """Türkçe uyumlu küçük harf: 'İ' → 'i', 'I' → 'ı' sorunlarını önler."""
    return metin.replace("İ", "i").replace("I", "ı").lower()


def _say(kelimeler, ingilizce: set, turkce_kokler: list) -> int:
    return sum(1 for k in kelimeler if k in ingilizce or any(k.startswith(t) for t in turkce_kokler))


def analyze_sentiment_lexicon(text: str) -> dict:
    """Kural tabanlı duygu skoru (API gerekmez). Skor -1 (çok olumsuz) ile +1 (çok olumlu) arası."""
    if not text:
        return {"score": 0.0, "label": "Nötr", "pos": 0, "neg": 0}

    # İngilizce için standart küçük harf, Türkçe için Türkçe kurallı küçük harf
    kelimeler = set(_KELIME.findall(text.lower())) | set(_KELIME.findall(_kucuk_harf(text)))
    pos = _say(kelimeler, POSITIVE_EN, POSITIVE_TR)
    neg = _say(kelimeler, NEGATIVE_EN, NEGATIVE_TR)
    total = pos + neg
    if total == 0:
        score, label = 0.0, "Nötr"
    else:
        score = (pos - neg) / total
        label = "Pozitif" if score > 0.1 else ("Negatif" if score < -0.1 else "Nötr")
    return {"score": score, "label": label, "pos": pos, "neg": neg}


def newsapi_anahtari():
    """NewsAPI anahtarını ortam değişkeninden veya Streamlit secrets'tan okur."""
    anahtar = os.getenv("NEWSAPI_KEY")
    if not anahtar:
        try:
            import streamlit as st
            anahtar = st.secrets.get("NEWSAPI_KEY")
        except Exception:
            anahtar = None
    return anahtar or None


def fetch_news(symbol: str, api_key: str = None, days_back: int = 7) -> list:
    """
    NewsAPI ile son haberleri çeker ve her başlığa duygu skoru ekler.
    Anahtar yoksa veya istek başarısız olursa örnek (demo) haberler döner;
    bu haberlerde "demo": True alanı bulunur.
    """
    api_key = api_key or newsapi_anahtari()
    if not api_key or api_key == "YOUR_API_KEY":
        return get_demo_news(symbol)

    clean_symbol = symbol.replace(".IS", "").replace(".F", "").replace("-USD", "").replace("-USDT", "")
    is_crypto = symbol.upper().endswith(("-USD", "-USDT"))
    params = {
        "q": f"{clean_symbol} cryptocurrency" if is_crypto else f"{clean_symbol} stock",
        "from": (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d"),
        "sortBy": "relevancy", "language": "en", "pageSize": 10, "apiKey": api_key,
    }
    try:
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=8)
        news = []
        for a in resp.json().get("articles", []):
            title = a.get("title", "") or ""
            desc = a.get("description", "") or ""
            news.append({
                "title": title[:120],
                "source": (a.get("source") or {}).get("name", "—"),
                "url": a.get("url", "#"),
                "published": (a.get("publishedAt") or "")[:10],
                "sentiment": analyze_sentiment_lexicon(title + " " + desc),
                "demo": False,
            })
        return news if news else get_demo_news(symbol)
    except Exception as e:
        print(f"Haber cekme hatasi: Veri saglayicisina ulasilamadi - {e}")
        return get_demo_news(symbol)


def get_demo_news(symbol: str) -> list:
    """
    API anahtarı yokken arayüzün nasıl çalıştığını göstermek için ÖRNEK başlıklar.
    Bunlar gerçek haber değildir; kaynak "Örnek veri" olarak işaretlenir ve
    duygu skoru doğrudan başlığın kendisinden hesaplanır.
    """
    clean = symbol.replace(".IS", "").replace("-USD", "").replace("-USDT", "")
    basliklar = [
        f"{clean} quarterly profit beats expectations on strong revenue growth",
        f"Market volatility raises concerns over {clean} outlook",
        f"{clean} announces expansion as sales rise",
        f"Analysts upgrade {clean} after record quarter",
        f"Rate uncertainty weighs on {clean}; analysts see downside risk",
    ]
    return [{
        "title": baslik,
        "source": "Örnek veri (demo)",
        "url": "#",
        "published": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
        "sentiment": analyze_sentiment_lexicon(baslik),
        "demo": True,
    } for i, baslik in enumerate(basliklar)]


def aggregate_sentiment(news_list: list) -> dict:
    """Haber listesinden genel duygu özeti."""
    if not news_list:
        return {"avg_score": 0.0, "positive": 0, "negative": 0, "neutral": 0,
                "overall": "Nötr", "demo": False}
    scores  = [n["sentiment"]["score"] for n in news_list]
    labels  = [n["sentiment"]["label"] for n in news_list]
    avg     = sum(scores) / len(scores)
    pos     = labels.count("Pozitif")
    neg     = labels.count("Negatif")
    neu     = labels.count("Nötr")
    overall = "Pozitif" if avg > 0.05 else ("Negatif" if avg < -0.05 else "Nötr")
    return {"avg_score": avg, "positive": pos, "negative": neg, "neutral": neu,
            "overall": overall, "demo": any(n.get("demo") for n in news_list)}
