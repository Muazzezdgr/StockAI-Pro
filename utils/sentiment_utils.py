"""
utils/sentiment_utils.py
Haber duygu analizi – NewsAPI + basit finans sözlük skoru.
"""
import re
import requests
from datetime import datetime, timedelta

# Finans odaklı pozitif/negatif kelime listeleri
POSITIVE_WORDS = [
    "growth", "profit", "gain", "surge", "rally", "beat", "strong",
    "record", "high", "bullish", "upgrade", "buy", "outperform",
    "revenue", "increase", "rise", "positive", "recovery", "boost",
    "yükseliş", "kazanç", "büyüme", "rekor", "güçlü", "artış"
]
NEGATIVE_WORDS = [
    "loss", "decline", "fall", "drop", "crash", "weak", "miss",
    "downgrade", "sell", "underperform", "cut", "risk", "concern",
    "negative", "bearish", "deficit", "layoff", "lawsuit",
    "düşüş", "kayıp", "zayıf", "risk", "endişe", "azalış"
]


def analyze_sentiment_lexicon(text: str) -> dict:
    """Kural tabanlı duygu skoru (API gerekmez)."""
    if not text:
        return {"score": 0.0, "label": "Nötr", "pos": 0, "neg": 0}

    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    total = pos + neg
    if total == 0:
        score, label = 0.0, "Nötr"
    else:
        score = (pos - neg) / total
        if score > 0.1:
            label = "Pozitif"
        elif score < -0.1:
            label = "Negatif"
        else:
            label = "Nötr"
    return {"score": score, "label": label, "pos": pos, "neg": neg}


def fetch_news(symbol: str, api_key: str = None, days_back: int = 7) -> list:
    """
    NewsAPI ile haber çek.
    api_key yoksa demo haberler döner.
    """
    # API anahtarı yoksa demo veri
    if not api_key or api_key == "YOUR_API_KEY":
        return get_demo_news(symbol)

    clean_symbol = symbol.replace(".IS", "").replace(".F", "")
    query = f"{clean_symbol} stock"
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={query}&from={from_date}&sortBy=relevancy"
        f"&language=en&pageSize=10&apiKey={api_key}"
    )
    try:
        resp = requests.get(url, timeout=8)
        data = resp.json()
        articles = data.get("articles", [])
        news = []
        for a in articles:
            title = a.get("title", "")
            desc  = a.get("description", "") or ""
            text  = title + " " + desc
            sent  = analyze_sentiment_lexicon(text)
            news.append({
                "title": title[:120],
                "source": a.get("source", {}).get("name", "—"),
                "url": a.get("url", "#"),
                "published": a.get("publishedAt", "")[:10],
                "sentiment": sent,
            })
        return news if news else get_demo_news(symbol)
    except Exception as e:
        print(f"Haber çekme hatası: {e}")
        return get_demo_news(symbol)


def get_demo_news(symbol: str) -> list:
    """API anahtarı olmadan gösterilecek örnek haberler."""
    clean = symbol.replace(".IS", "")
    demos = [
        {
            "title": f"{clean} quarterly earnings exceed analyst expectations",
            "source": "Financial Times",
            "url": "#",
            "published": datetime.now().strftime("%Y-%m-%d"),
            "sentiment": analyze_sentiment_lexicon("earnings exceed positive growth strong"),
        },
        {
            "title": f"Market volatility impacts {clean} stock performance",
            "source": "Reuters",
            "url": "#",
            "published": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "sentiment": analyze_sentiment_lexicon("volatility risk decline concern negative"),
        },
        {
            "title": f"{clean} announces expansion into new markets",
            "source": "Bloomberg",
            "url": "#",
            "published": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "sentiment": analyze_sentiment_lexicon("expansion growth positive increase revenue"),
        },
        {
            "title": f"Analysts upgrade {clean} to buy with raised price target",
            "source": "WSJ",
            "url": "#",
            "published": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "sentiment": analyze_sentiment_lexicon("upgrade buy outperform positive bullish"),
        },
        {
            "title": f"Global economic uncertainty weighs on {clean} outlook",
            "source": "CNBC",
            "url": "#",
            "published": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "sentiment": analyze_sentiment_lexicon("uncertainty weak risk concern decline"),
        },
    ]
    return demos


def aggregate_sentiment(news_list: list) -> dict:
    """Haber listesinden genel duygu özeti."""
    if not news_list:
        return {"avg_score": 0.0, "positive": 0, "negative": 0, "neutral": 0, "overall": "Nötr"}
    scores  = [n["sentiment"]["score"] for n in news_list]
    labels  = [n["sentiment"]["label"] for n in news_list]
    avg     = sum(scores) / len(scores)
    pos     = labels.count("Pozitif")
    neg     = labels.count("Negatif")
    neu     = labels.count("Nötr")
    overall = "Pozitif" if avg > 0.05 else ("Negatif" if avg < -0.05 else "Nötr")
    return {"avg_score": avg, "positive": pos, "negative": neg, "neutral": neu, "overall": overall}
