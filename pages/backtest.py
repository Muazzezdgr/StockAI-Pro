"""
pages/backtest.py  –  Strateji Backtest Sayfası
Değerlendirme: Canlı demo / kullanıcı etkileşimi
"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np

from utils.data_utils import fetch_stock_data, prepare_rf_data
from utils.model_utils import train_random_forest
from utils.chart_theme import (COLORS as C, FONT_FAMILY, PLOT_BG,
    LINE_THIN, LINE_MAIN, TITLE_SIZE, base_axis, bottom_legend,
    hover_style, rgba, area_fillgradient, modebar_config)

def _card(col, label, value, sub="", color=None):
    color = color or C["accent"]
    with col:
        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {C['border']};
                    border-left:3px solid {color};border-radius:10px;
                    padding:0.85rem 1rem;margin-bottom:0.5rem;">
          <div style="color:{C['muted']};font-size:0.7rem;font-family:'Space Mono',monospace;
                      letter-spacing:1px;text-transform:uppercase;">{label}</div>
          <div style="color:{C['text']};font-size:1.35rem;font-weight:700;
                      font-family:'Space Mono',monospace;margin:4px 0;">{value}</div>
          <div style="color:{color};font-size:0.74rem;">{sub}</div>
        </div>""", unsafe_allow_html=True)

def show_backtest(symbol, period, interval="1d"):
    st.markdown('<p class="section-title">// STRATEJİ BACKTEST SİMÜLASYONU</p>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-left:3px solid {C['yellow']};border-radius:10px;
                padding:1rem 1.4rem;margin-bottom:1.2rem;font-size:0.85rem;
                color:{C['muted']};line-height:1.8;">
      <b style="color:{C['yellow']}">Backtest Nedir?</b>
      Model tahminlerine göre hisse alım/satım yapıldığında elde edilecek
      getiriyi geçmiş veriyle simüle eder. <b style="color:{C['text']}">
      Buy &amp; Hold</b> stratejisiyle karşılaştırılır.
    </div>""", unsafe_allow_html=True)

    # Parametreler
    c1,c2,c3 = st.columns(3)
    initial  = c1.number_input("💰 Başlangıç Sermayesi ($)", 1000, 100000, 10000, 1000)
    thresh   = c2.slider("📊 Alım Eşiği (Model Güven %)", 50, 80, 60)
    stoploss = c3.slider("🛑 Stop Loss (%)", 1, 20, 5)

    if not st.button("▶  BACKTEST ÇALIŞTIR", use_container_width=True):
        st.info("ℹ️  Parametreleri ayarlayıp BACKTEST ÇALIŞTIR butonuna tıklayın.")
        return

    try:
        with st.spinner("Veri ve model hazırlanıyor..."):
            df = fetch_stock_data(symbol, period, interval=interval)
            if df is None or df.empty:
                st.error(f"Bu sembol icin veri bulunamadi. Lutfen sembolu kontrol edin: {symbol}"); return
            X_train,X_test,y_train,y_test,scaler,_ = prepare_rf_data(df)
            model = train_random_forest(X_train, y_train)
            probs = model.predict_proba(X_test)[:,1]
    except Exception as e:
        st.error(f"Veri saglaycisina ulasilamadi. Lutfen birkac dakika sonra tekrar deneyin.")
        return

    split  = int(len(df) * 0.8)
    n      = min(len(probs), len(df) - split)
    prices = df["Close"].iloc[split:split+n].values
    probs  = probs[:n]

    # ── Backtest simülasyonu ──────────────────────────────────────────────────
    capital   = float(initial)
    position  = 0.0
    portfolio = []
    buy_hold  = [float(initial) / prices[0] * p for p in prices]
    trades    = 0
    wins      = 0
    entry_price = 0.0
    trade_log = []

    for i, (price, prob) in enumerate(zip(prices, probs)):
        # Alım sinyali
        if prob > thresh/100 and position == 0:
            position    = capital / price
            capital     = 0.0
            entry_price = price
            trades     += 1

        # Satım sinyali veya stop-loss
        elif position > 0:
            loss_pct = (price - entry_price) / entry_price * 100
            if prob < (1 - thresh/100) or loss_pct < -stoploss:
                capital  = position * price
                won      = price > entry_price
                wins    += int(won)
                trade_log.append({
                    "gün": i,
                    "giriş": entry_price,
                    "çıkış": price,
                    "kar": (price-entry_price)/entry_price*100,
                    "sonuç": "✅ Kar" if won else "❌ Zarar",
                })
                position = 0.0

        portfolio.append(capital + position * price)

    # Son açık pozisyonu kapat
    if position > 0:
        portfolio[-1] = position * prices[-1]

    final_m  = portfolio[-1]
    final_bh = buy_hold[-1]
    ret_m    = (final_m  - initial) / initial * 100
    ret_bh   = (final_bh - initial) / initial * 100
    win_rate = (wins / trades * 100) if trades > 0 else 0

    # Period length (days) used for annualization and Sharpe calculation
    period_days = len(portfolio)

    # Annualized return (assume daily data -> 252 trading days per year)
    if period_days > 0 and initial > 0:
        try:
            ann_return = (final_m / initial) ** (252.0 / max(period_days, 1)) - 1.0
        except Exception:
            ann_return = None
    else:
        ann_return = None

    # Sharpe Ratio (assume risk-free rate = 0). Use daily returns and annualize.
    sharpe = None
    if len(portfolio) > 1:
        arr = np.array(portfolio, dtype=float)
        daily_rets = np.diff(arr) / arr[:-1]
        if daily_rets.size > 1:
            mean_d = daily_rets.mean()
            std_d = daily_rets.std(ddof=1)
            if std_d > 0:
                sharpe = (mean_d / std_d) * np.sqrt(252.0)
            else:
                sharpe = None
        else:
            sharpe = None
    else:
        sharpe = None

    # Max drawdown
    peak = np.maximum.accumulate(portfolio)
    dd   = (np.array(portfolio) - peak) / peak * 100
    max_dd = float(dd.min())

    # ── Sonuç kartları ────────────────────────────────────────────────────────
    mc1,mc2,mc3,mc4,mc5 = st.columns(5)
    _card(mc1,"📈 Model Getiri", f"{ret_m:+.1f}%",
          color=C["green"] if ret_m>0 else C["red"])
    _card(mc2,"📊 Buy&Hold",    f"{ret_bh:+.1f}%",
          color=C["green"] if ret_bh>0 else C["red"])
    _card(mc3,"⚡ Fark",        f"{ret_m-ret_bh:+.1f}%",
          color=C["green"] if ret_m>ret_bh else C["red"])
    _card(mc4,"🎯 Kazanma Oranı",f"{win_rate:.0f}%",
          sub=f"{trades} işlem",
          color=C["green"] if win_rate>50 else C["yellow"])
    _card(mc5,"📉 Max Drawdown",f"{max_dd:.1f}%",
          color=C["red"] if max_dd < -10 else C["yellow"])

    # Ek metrikler: Sharpe ve Yıllıklandırılmış Getiri
    sc1, sc2 = st.columns(2)
    sharpe_text = f"{sharpe:.2f}" if sharpe is not None else "—"
    ann_text = f"{ann_return*100:+.2f}%" if ann_return is not None else "—"
    _card(sc1, "Sharpe Ratio", sharpe_text,
          sub="Risk-free rate = 0 varsayildi", color=C["accent"])
    _card(sc2, "Yıllıklandırılmış Getiri", ann_text,
          sub="Dönem bazlı sonuç yıllıklandırıldı", color=C["purple"]) 

    # Uyarılar ve açıklamalar
    if trades < 5:
        st.warning("Az sayıda işlem nedeniyle bu sonuclar istatistiksel olarak anlamli degildir, yorumlarken dikkatli olun.")

    st.markdown("<div style='color:%s;font-size:0.85rem;'>" % C["muted"] +
                "Kazanma oranı (trade başına başarı) ile toplam getiri farklı metriklerdir; " +
                "kazanma oranı düşük olsa dahi büyük kazançlı işlemler toplam getiriyi pozitif yapabilir, " +
                "veya tersi de geçerlidir. Bu iki metriği birlikte değerlendiriniz." +
                "</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Ana grafik ────────────────────────────────────────────────────────────
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=portfolio, mode="lines",
        name=f"Model ({ret_m:+.1f}%)",
        line=dict(color=C["accent"], width=LINE_MAIN),
        fill="tozeroy", fillgradient=area_fillgradient(C["accent"], 0.20, 0.0),
        hovertemplate="Gün %{x}<br>Portföy: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        y=buy_hold, mode="lines",
        name=f"Buy&Hold ({ret_bh:+.1f}%)",
        line=dict(color=C["purple"], width=LINE_THIN, dash="dash"),
        hovertemplate="Gün %{x}<br>B&H: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=initial, line_dash="dot", line_width=1,
                  line_color=C["muted"], opacity=0.5,
                  annotation_text="Başlangıç",
                  annotation_font=dict(size=10, color=C["muted"], family=FONT_FAMILY))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(color=C["text"], family=FONT_FAMILY, size=10.5),
        margin=dict(l=58, r=24, t=52, b=56),
        title=dict(text=f"<b>{symbol}</b> — Model vs Buy&Hold",
                   font=dict(size=TITLE_SIZE, color=C["text"]), x=0.01, xanchor="left"),
        height=400,
        xaxis=base_axis("Gün"),
        yaxis=base_axis("Portföy Değeri ($)"),
        legend=bottom_legend(),
        hovermode="x unified",
        hoverlabel=hover_style(),
    )
    st.plotly_chart(fig, use_container_width=True, config=modebar_config(f"{symbol}_backtest"))

    # ── İşlem geçmişi ─────────────────────────────────────────────────────────
    if trade_log:
        st.markdown(f"""
        <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                    text-transform:uppercase;margin-bottom:0.6rem;">
          İşlem Geçmişi (Son {min(8,len(trade_log))} işlem)
        </div>""", unsafe_allow_html=True)

        rows = "".join(
            f'<tr style="border-bottom:1px solid {C["border"]};">'
            f'<td style="padding:6px 8px;color:{C["muted"]}">Gün {t["gün"]}</td>'
            f'<td style="padding:6px 8px;color:{C["text"]}">${t["giriş"]:.2f}</td>'
            f'<td style="padding:6px 8px;color:{C["text"]}">${t["çıkış"]:.2f}</td>'
            f'<td style="padding:6px 8px;color:{"#10b981" if t["kar"]>0 else "#ef4444"}">'
            f'{t["kar"]:+.2f}%</td>'
            f'<td style="padding:6px 8px">{t["sonuç"]}</td>'
            f'</tr>'
            for t in trade_log[-8:]
        )
        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {C['border']};
                    border-radius:10px;padding:1rem;overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;
                        font-family:'Space Mono',monospace;font-size:0.8rem;">
            <tr style="color:{C['muted']};border-bottom:1px solid {C['border']};">
              <th style="padding:6px 8px;text-align:left">Tarih</th>
              <th style="padding:6px 8px;text-align:left">Giriş</th>
              <th style="padding:6px 8px;text-align:left">Çıkış</th>
              <th style="padding:6px 8px;text-align:left">Kar/Zarar</th>
              <th style="padding:6px 8px;text-align:left">Sonuç</th>
            </tr>
            {rows}
          </table>
        </div>""", unsafe_allow_html=True)
