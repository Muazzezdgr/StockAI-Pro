
import streamlit as st

st.set_page_config(
    page_title="StockAI Pro — Hisse Tahmin Sistemi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --border: #1e2d45;
    --accent: #00d4ff;
    --accent2: #7c3aed;
    --green: #10b981;
    --red: #ef4444;
    --yellow: #f59e0b;
    --text: #e2e8f0;
    --muted: #64748b;
    --font-main: 'Syne', sans-serif;
    --font-mono: 'Space Mono', monospace;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-main) !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0,212,255,0.3) !important;
}

[data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), var(--accent2));
}

.section-title {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

.signal-up {
    color: var(--green);
    font-weight: 700;
    font-family: var(--font-mono);
}
.signal-down {
    color: var(--red);
    font-weight: 700;
    font-family: var(--font-mono);
}

.news-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.news-card:hover { border-color: var(--accent); }

.positive-sentiment { border-left: 3px solid var(--green); }
.negative-sentiment { border-left: 3px solid var(--red); }
.neutral-sentiment  { border-left: 3px solid var(--yellow); }

.progress-bar {
    height: 6px;
    border-radius: 3px;
    background: var(--border);
    margin-top: 0.5rem;
}
.progress-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, var(--accent2), var(--accent));
}

.logo-text {
    font-family: var(--font-mono);
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
}

.stSelectbox > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

.stSlider [data-baseweb="slider"] {
    margin-top: 0.5rem;
}

div[data-testid="stExpander"] {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

.status-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-buy  { background: rgba(16,185,129,0.15); color: var(--green); border: 1px solid var(--green); }
.badge-sell { background: rgba(239,68,68,0.15);  color: var(--red);   border: 1px solid var(--red);   }
.badge-hold { background: rgba(245,158,11,0.15); color: var(--yellow);border: 1px solid var(--yellow);}
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text">STOCK AI PRO</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b;font-size:0.75rem;margin-top:4px;font-family:Space Mono,monospace;">v2.0 — LSTM + RF + NLP</p>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "NAVİGASYON",
        ["📊  Dashboard", "🤖  Model Eğitimi", "📰  Haber Analizi", "📈  Backtest", "📋  Hakkında"],
        label_visibility="visible"
    )

    st.markdown("---")
    st.markdown('<p class="section-title">Sembol Seçimi</p>', unsafe_allow_html=True)

    market = st.selectbox("Piyasa", ["ABD (NASDAQ/NYSE)", "BIST (Türkiye)", "Kripto Para"])

    if "ABD" in market:
        symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "NFLX"]
    elif "BIST" in market:
        symbols = ["THYAO.IS", "GARAN.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS", "BIMAS.IS", "SISE.IS", "TUPRS.IS"]
    else:
        symbols = ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "LTC-USD"]

    selected_symbol = st.selectbox("Sembol", symbols)
    period = st.selectbox("Veri Periyodu", ["1y", "2y", "3y", "5y"], index=1)
    window_size = st.slider("LSTM Pencere Boyutu", 20, 60, 30)

    st.markdown("---")
    run_analysis = st.button("🚀  ANALİZİ BAŞLAT", use_container_width=True)

# ── Route to pages ───────────────────────────────────────────────────────────
if "📊" in page:
    from pages.dashboard import show_dashboard
    show_dashboard(selected_symbol, period, window_size, run_analysis)
elif "🤖" in page:
    from pages.model_training import show_model_training
    show_model_training(selected_symbol, period, window_size)
elif "📰" in page:
    from pages.news_analysis import show_news_analysis
    show_news_analysis(selected_symbol)
elif "📈" in page:
    from pages.backtest import show_backtest
    show_backtest(selected_symbol, period)
elif "📋" in page:
    from pages.about import show_about
    show_about()
