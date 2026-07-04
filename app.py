
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
@media (max-width: 900px) {
    .stButton > button { padding: 0.45rem 0.9rem !important; font-size: 0.85rem !important; }
    .metric-card, .news-card { padding: 0.7rem 0.9rem !important; }
    .logo-text { font-size: 1.05rem !important; }
    .section-title { font-size: 0.65rem !important; }
    /* help columns avoid overflow on narrow screens */
    div[role="list"] > div[role="listitem"] { min-width: 0 !important; }
}
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

[data-testid="stPageListContainer"] {
    display: none !important;
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
    # Sidebar summary: portfolio total and active alarms (quick glance)
    try:
        total_portfolio = 0.0
        if "portfolio" in st.session_state and st.session_state["portfolio"]:
            for item in st.session_state.get("portfolio", []):
                qty = float(item.get("quantity", 0) or 0)
                # prefer item-level cached current price if available
                cur = item.get("current_price") if item.get("current_price") is not None else None
                if cur is None:
                    # fallback to cost (buy_price) to avoid slow network calls in sidebar
                    cur = item.get("buy_price", 0)
                total_portfolio += qty * float(cur)
        active_alarms = len([a for a in st.session_state.get("alarms", []) if a.get("status") != "tetiklendi"]) if "alarms" in st.session_state else 0
        st.markdown(f"""
        <div class="metric-card" style="padding:0.6rem 1rem;margin-bottom:0.75rem;">
          <div style="color:var(--muted);font-size:0.72rem;">Portföy</div>
          <div style="font-weight:800;font-family:var(--font-mono);font-size:1rem;color:var(--text);">
            {total_portfolio:,.0f} TL &nbsp;|&nbsp; {active_alarms} Aktif Alarm
          </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass
    st.markdown("---")

    page = st.radio(
        "NAVİGASYON",
        ["📊  Dashboard", "🤖  Model Eğitimi", "📰  Haber Analizi", "📈  Backtest", "💼  Portföyüm", "⏰  Alarmlar", "Yasal Uyari"],
        label_visibility="visible",
        key="nav_page"
    )

    st.markdown("---")
    st.markdown('<p class="section-title">Sembol Seçimi</p>', unsafe_allow_html=True)

    market = st.selectbox("Piyasa", ["ABD (NASDAQ/NYSE)", "BIST (Türkiye)", "Kripto Para"])

    if "ABD" in market:
        symbols = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "NFLX"]
    elif "BIST" in market:
        symbols = ["THYAO.IS", "GARAN.IS", "AKBNK.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS", "BIMAS.IS", "SAHOL.IS", "SISE.IS", "TUPRS.IS", "PGSUS.IS", "FROTO.IS", "TOASO.IS", "ARCLK.IS", "TCELL.IS", "YKBNK.IS", "ISCTR.IS", "VAKBN.IS", "HALKB.IS", "KOZAL.IS", "PETKM.IS", "TTKOM.IS", "MGROS.IS", "ULKER.IS", "TAVHL.IS", "ENKAI.IS", "EKGYO.IS", "SASA.IS", "DOHOL.IS", "KOZAA.IS"]
    else:
        symbols = ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "LTC-USD"]

    selected_symbol = st.selectbox("Sembol", symbols)
    selected_period = st.selectbox("Veri Periyodu", ["1h", "1y", "2y", "3y", "5y"], index=1)
    interval = "1h" if selected_period == "1h" else "1d"
    effective_period = "2y" if interval == "1h" else selected_period
    window_size = st.slider("LSTM Pencere Boyutu", 20, 60, 30)

    if selected_period == "1h":
        st.info("⚠️ Saatlik veri daha güncel sinyaller verir ancak kısa vadeli gürültüye (noise) daha duyarlıdır; model güven skorunu buna göre yorumlayın.")

    st.markdown("---")
    run_analysis = st.button("🚀  ANALİZİ BAŞLAT", use_container_width=True)

# ── Route to pages ───────────────────────────────────────────────────────────
if "📊" in page:
    from pages.dashboard import show_dashboard
    show_dashboard(selected_symbol, effective_period, window_size, run_analysis, interval=interval)
elif "🤖" in page:
    from pages.model_training import show_model_training
    show_model_training(selected_symbol, effective_period, window_size, interval=interval)
elif "📰" in page:
    from pages.news_analysis import show_news_analysis
    show_news_analysis(selected_symbol)
elif "📈" in page:
    from pages.backtest import show_backtest
    show_backtest(selected_symbol, effective_period, interval=interval)
elif "💼" in page:
    from pages.portfolio import show_portfolio
    show_portfolio()
elif "⏰" in page:
    from pages.alarms import show_alarms
    show_alarms()
elif "Yasal Uyari" in page:
    from pages.disclaimer import show_disclaimer
    show_disclaimer()

