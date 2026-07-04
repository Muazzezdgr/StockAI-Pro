"""
pages/comparison.py  -  Karsilastirmali Analiz
"""
import streamlit as st
import plotly.graph_objects as go

from utils.data_utils import fetch_stock_data, get_ticker_info, prepare_rf_data
from utils.model_utils import train_random_forest
from utils.chart_theme import (COLORS as C, LINE_REG, base_layout as pl,
    modebar_config)

US_SYMBOLS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "NFLX"]
BIST_SYMBOLS = ["THYAO.IS", "GARAN.IS", "AKBNK.IS", "ASELS.IS", "KCHOL.IS", "EREGL.IS", "BIMAS.IS",
                "SAHOL.IS", "SISE.IS", "TUPRS.IS", "PGSUS.IS", "FROTO.IS", "TOASO.IS", "ARCLK.IS",
                "TCELL.IS", "YKBNK.IS", "ISCTR.IS", "VAKBN.IS", "HALKB.IS", "KOZAL.IS", "PETKM.IS",
                "TTKOM.IS", "MGROS.IS", "ULKER.IS", "TAVHL.IS", "ENKAI.IS", "EKGYO.IS", "SASA.IS",
                "DOHOL.IS", "KOZAA.IS"]
CRYPTO_SYMBOLS = ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "LTC-USD"]

MARKETS = {
    "ABD (NASDAQ/NYSE)": US_SYMBOLS,
    "BIST (Turkiye)": BIST_SYMBOLS,
    "Kripto Para": CRYPTO_SYMBOLS,
}


def _card(col, label, value, sub="", color=None):
    color = color or C["accent"]
    with col:
        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {C['border']};
                    border-left:3px solid {color};border-radius:10px;
                    padding:0.85rem 1rem;margin-bottom:0.5rem;">
          <div style="color:{C['muted']};font-size:0.7rem;
                      font-family:'Space Mono',monospace;
                      letter-spacing:1px;text-transform:uppercase;">{label}</div>
          <div style="color:{C['text']};font-size:1.35rem;font-weight:700;
                      font-family:'Space Mono',monospace;margin:4px 0;">{value}</div>
          <div style="color:{color};font-size:0.74rem;">{sub}</div>
        </div>""", unsafe_allow_html=True)


def _fmt_price(value, currency):
    if currency == "USD":
        return f"${value:,.2f}"
    if currency == "TRY":
        return f"{value:,.2f} TL"
    return f"{value:,.2f} {currency}"


def _quick_predict(df):
    try:
        X_train, X_test, y_train, _, _, _ = prepare_rf_data(df)
        m = train_random_forest(X_train, y_train, n_estimators=80)
        return float(m.predict_proba(X_test[-1:])[0][1])
    except Exception:
        return 0.5


def _symbol_picker(label_suffix, default_market, default_symbol):
    st.markdown(f'<p style="color:{C["muted"]};font-size:0.75rem;'
                f'font-family:Space Mono,monospace;letter-spacing:1px;'
                f'text-transform:uppercase;margin-bottom:0.3rem;">Varlik {label_suffix}</p>',
                unsafe_allow_html=True)
    market_keys = list(MARKETS.keys())
    market = st.selectbox(f"Piyasa {label_suffix}", market_keys,
                           index=market_keys.index(default_market),
                           key=f"cmp_market_{label_suffix}")
    symbols = MARKETS[market]
    default_idx = symbols.index(default_symbol) if default_symbol in symbols else 0
    symbol = st.selectbox(f"Sembol {label_suffix}", symbols, index=default_idx,
                           key=f"cmp_symbol_{label_suffix}")
    return symbol


def _metrics_for(symbol, period, interval):
    df = fetch_stock_data(symbol, period, interval=interval)
    if df is None or df.empty:
        return None
    try:
        info = get_ticker_info(symbol)
    except Exception:
        info = {"name": symbol, "currency": "USD"}

    last  = float(df["Close"].iloc[-1])
    first = float(df["Close"].iloc[0])
    period_return = (last / first - 1) * 100
    volatility = float(df["Return"].std() * 100)
    rsi_v = float(df["RSI"].iloc[-1])
    norm = (df["Close"] / first - 1) * 100
    confidence = _quick_predict(df)

    return {
        "symbol": symbol,
        "name": info.get("name", symbol),
        "currency": info.get("currency", "USD"),
        "df": df,
        "last": last,
        "period_return": period_return,
        "volatility": volatility,
        "rsi": rsi_v,
        "norm": norm,
        "confidence": confidence,
    }


def _generate_summary(a, b):
    if abs(a["period_return"] - b["period_return"]) < 1e-9:
        perf_line = f"{a['symbol']} ve {b['symbol']} bu donemde birbirine yakin bir getiri sergilemistir."
    else:
        winner = a if a["period_return"] > b["period_return"] else b
        loser  = b if winner is a else a
        perf_line = (
            f"{winner['symbol']}, bu donemde {winner['period_return']:+.2f}% getiri ile "
            f"{loser['symbol']} ({loser['period_return']:+.2f}%) sembolune gore daha iyi "
            f"performans gostermistir."
        )

    if abs(a["volatility"] - b["volatility"]) < 1e-9:
        vol_line = "Iki varligin volatilitesi bu donemde birbirine yakin seviyededir."
    else:
        more_volatile = a if a["volatility"] > b["volatility"] else b
        less_volatile = b if more_volatile is a else a
        vol_line = (
            f"Volatilite acisindan {more_volatile['symbol']} (gunluk getiri std. sapmasi "
            f"%{more_volatile['volatility']:.2f}), {less_volatile['symbol']} sembolune "
            f"gore (%{less_volatile['volatility']:.2f}) daha dalgali bir seyir izlemistir."
        )

    conf_diff = abs(a["confidence"] - b["confidence"])
    if conf_diff < 0.02:
        conf_line = "Model guven skorlari iki varlik icin de birbirine yakin cikmistir."
    else:
        more_conf = a if a["confidence"] > b["confidence"] else b
        conf_line = (
            f"Model, {more_conf['symbol']} icin daha yuksek bir yukari yonlu guven skoru "
            f"(%{more_conf['confidence']*100:.1f}) uretmistir."
        )

    return perf_line + " " + vol_line + " " + conf_line


def _row(label, va, vb, fmt="{:.2f}", highlight=None):
    ca = cb = C["text"]
    if highlight is True:
        ca = C["green"] if va > vb else (C["red"] if va < vb else C["text"])
        cb = C["green"] if vb > va else (C["red"] if vb < va else C["text"])
    elif highlight is False:
        ca = C["green"] if va < vb else (C["red"] if va > vb else C["text"])
        cb = C["green"] if vb < va else (C["red"] if vb > va else C["text"])
    return f"""<tr style="border-bottom:1px solid {C['border']};">
      <td style="padding:8px 6px;color:{C['muted']};">{label}</td>
      <td style="padding:8px 6px;color:{ca};font-family:'Space Mono',monospace;">{fmt.format(va)}</td>
      <td style="padding:8px 6px;color:{cb};font-family:'Space Mono',monospace;">{fmt.format(vb)}</td>
    </tr>"""


def show_comparison(period, interval):
    st.markdown('<p class="section-title">// KARSILASTIRMALI ANALIZ</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="color:{C['muted']};font-size:0.75rem;
                font-family:'Space Mono',monospace;padding-bottom:0.6rem;">
      Iki farkli sembolu (hisse, kripto veya BIST) ayni donem uzerinden karsilastirin.
      Bu sayfa egitim ve bilgilendirme amaclidir, yatirim tavsiyesi degildir.
    </div>""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        symbol_a = _symbol_picker("A", "ABD (NASDAQ/NYSE)", "AAPL")
    with col_b:
        symbol_b = _symbol_picker("B", "Kripto Para", "BTC-USD")

    run = st.button("KARSILASTIR", use_container_width=True, key="cmp_run")

    if not run:
        st.markdown(f"""
        <div style="text-align:center;padding:2.5rem 1rem;">
          <div style="font-family:'Space Mono',monospace;
                     background:linear-gradient(135deg,{C['accent']},{C['purple']});
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     font-size:1.6rem;font-weight:700;">Karsilastirmali Analiz</div>
          <p style="color:{C['muted']};max-width:480px;margin:0.8rem auto 0;
                    line-height:1.8;font-size:0.92rem;">
            Yukaridan iki varlik secip <b style="color:{C['accent']}">KARSILASTIR</b>
            butonuna tiklayin. Farkli fiyat araliklarindaki varliklar yuzde
            degisim uzerinden ayni grafikte karsilastirilir.
          </p>
        </div>""", unsafe_allow_html=True)
        return

    if symbol_a == symbol_b:
        st.warning("Lutfen birbirinden farkli iki sembol secin.")
        return

    try:
        with st.spinner("Veri cekiliyor ve modeller egitiliyor..."):
            a = _metrics_for(symbol_a, period, interval)
            b = _metrics_for(symbol_b, period, interval)
    except Exception:
        st.error("Veri saglayicisina ulasilamadi. Lutfen birkac dakika sonra tekrar deneyin.")
        return

    if a is None:
        st.error(f"Bu sembol icin veri bulunamadi. Lutfen sembolu kontrol edin: {symbol_a}")
        return
    if b is None:
        st.error(f"Bu sembol icin veri bulunamadi. Lutfen sembolu kontrol edin: {symbol_b}")
        return

    # -- Ust kartlar: guncel fiyat ve donem getirisi --------------------------
    c1, c2, c3, c4 = st.columns(4)
    _card(c1, f"{a['symbol']} Fiyat", _fmt_price(a["last"], a["currency"]),
          sub=a["name"], color=C["accent"])
    _card(c2, f"{a['symbol']} Donem Getirisi", f"{a['period_return']:+.2f}%",
          color=C["green"] if a["period_return"] >= 0 else C["red"])
    _card(c3, f"{b['symbol']} Fiyat", _fmt_price(b["last"], b["currency"]),
          sub=b["name"], color=C["purple"])
    _card(c4, f"{b['symbol']} Donem Getirisi", f"{b['period_return']:+.2f}%",
          color=C["green"] if b["period_return"] >= 0 else C["red"])

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # -- Normalize yuzde degisim grafigi ---------------------------------------
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a["df"].index, y=a["norm"], name=a["symbol"],
        line=dict(color=C["accent"], width=LINE_REG),
        hovertemplate=f"{a['symbol']}: %{{y:+.2f}}%<extra></extra>"))
    fig.add_trace(go.Scatter(x=b["df"].index, y=b["norm"], name=b["symbol"],
        line=dict(color=C["purple"], width=LINE_REG),
        hovertemplate=f"{b['symbol']}: %{{y:+.2f}}%<extra></extra>"))
    fig.add_hline(y=0, line_dash="dash", line_width=1, line_color=C["muted"], opacity=0.5)
    fig.update_layout(**pl(f"<b>{a['symbol']} vs {b['symbol']}</b> - Yuzde Degisim (Normalize)",
                           height=430, y_title="Yuzde Degisim (%)"),
                      hovermode="x unified", dragmode="zoom")
    st.plotly_chart(fig, use_container_width=True,
                     config=modebar_config(f"{a['symbol']}_vs_{b['symbol']}"))

    # -- Metrik karsilastirma tablosu ------------------------------------------
    rows = "".join([
        _row("Guncel Fiyat", a["last"], b["last"], fmt="{:,.2f}"),
        _row("Donem Getirisi (%)", a["period_return"], b["period_return"], fmt="{:+.2f}", highlight=True),
        _row("Volatilite (gunluk std. %)", a["volatility"], b["volatility"], fmt="{:.2f}", highlight=False),
        _row("RSI (14)", a["rsi"], b["rsi"], fmt="{:.1f}"),
        _row("Model Guven (%)", a["confidence"] * 100, b["confidence"] * 100, fmt="{:.1f}", highlight=True),
    ])

    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-radius:10px;padding:1.1rem 1.5rem;margin-top:4px;">
      <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:0.8rem;">
        Metrik Karsilastirmasi
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
        <tr style="color:{C['muted']};border-bottom:1px solid {C['border']};">
          <td style="padding:6px;font-family:'Space Mono',monospace;font-size:0.72rem;
                     text-transform:uppercase;letter-spacing:1px;">Metrik</td>
          <td style="padding:6px;color:{C['accent']};font-family:'Space Mono',monospace;
                     font-size:0.78rem;">{a['symbol']}</td>
          <td style="padding:6px;color:{C['purple']};font-family:'Space Mono',monospace;
                     font-size:0.78rem;">{b['symbol']}</td>
        </tr>
        {rows}
      </table>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # -- Otomatik ozet ----------------------------------------------------------
    summary = _generate_summary(a, b)
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{C['s1']},{C['s2']});
                border:1px solid {C['border']};border-left:3px solid {C['accent']};
                border-radius:10px;padding:1.1rem 1.4rem;margin-bottom:1rem;">
      <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:0.6rem;">
        Otomatik Ozet
      </div>
      <div style="color:{C['text']};font-size:0.92rem;line-height:1.7;">
        {summary}
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid {C['border']};
                color:{C['muted']};font-size:0.75rem;font-family:'Space Mono',monospace;">
      Veri kaynagi: Yahoo Finance. Bu sayfadaki bilgiler yatirim tavsiyesi degildir.
    </div>""", unsafe_allow_html=True)
