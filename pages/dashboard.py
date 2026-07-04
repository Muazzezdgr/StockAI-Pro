"""
pages/dashboard.py  –  Ana Dashboard  (v3 – yaxis çakışması yok)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

from utils.data_utils import (fetch_stock_data, get_ticker_info,
    format_market_cap, compute_signal, prepare_rf_data)
from utils.sentiment_utils import fetch_news, aggregate_sentiment
from utils.model_utils import train_random_forest, evaluate_model, get_feature_importance
from utils.pdf_report import generate_pdf_report
from utils.chart_theme import (COLORS as C, FONT_FAMILY, PLOT_BG,
    LINE_HAIR, LINE_THIN, LINE_REG, LINE_MAIN,
    TITLE_SIZE, AXIS_TITLE, TICK_SIZE, base_layout as pl, base_axis,
    bottom_legend, hover_style, rgba, area_fillgradient, modebar_config)

# ════════════════════════════════════════════════════════════════════════════
def show_dashboard(symbol, period, window_size, run_analysis, interval="1d"):
    st.markdown('<p class="section-title">// ANA DASHBOARD</p>',
                unsafe_allow_html=True)
    _disclaimer_note()
    if not run_analysis:
        _welcome(); return

    # Veri çekme - hata yönetimi ile
    try:
        with st.spinner(f"Veri çekiliyor..."):
            df = fetch_stock_data(symbol, period, interval=interval)
        if df is None or df.empty:
            st.error(f"Bu sembol icin veri bulunamadi. Lutfen sembolu kontrol edin: {symbol}")
            return
        last_update = datetime.now()
    except Exception as e:
        st.error(f"Veri saglaycisina ulasilamadi. Lutfen birkac dakika sonra tekrar deneyin.")
        return

    # Ticker bilgisi - hata tolere et
    try:
        info = get_ticker_info(symbol)
    except Exception:
        info = {"name": symbol, "sector": "—"}

    # Haber analizi - hata tolere et
    try:
        news = fetch_news(symbol)
        sent_agg = aggregate_sentiment(news)
    except Exception:
        news = []
        sent_agg = {"positive": 0, "negative": 0, "neutral": 0, "overall": "Nötr", "avg_score": 0.0}

    last   = float(df["Close"].iloc[-1])
    prev   = float(df["Close"].iloc[-2])
    change = (last - prev) / prev * 100
    rsi_v  = float(df["RSI"].iloc[-1])
    macd_h = float(df["MACD_Hist"].iloc[-1])
    bb_pos = float(df["BB_Pos"].iloc[-1])

    with st.spinner("🤖  Model tahmin üretiyor..."):
        pred_prob = _quick_predict(df)

    signal, badge_cls = compute_signal(rsi_v, macd_h, bb_pos, pred_prob)
    chg_color = C["green"] if change >= 0 else C["red"]
    arrow     = "▲" if change >= 0 else "▼"

    # ── Hero Kartı ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{C['s1']},{C['s2']});
                border:1px solid {C['border']};border-radius:16px;
                padding:1.6rem 2rem;margin-bottom:1.2rem;
                box-shadow:0 4px 32px rgba(0,0,0,0.5);">
      <div style="display:flex;justify-content:space-between;
                  align-items:center;flex-wrap:wrap;gap:1rem;">
        <div>
          <div style="font-family:'Space Mono',monospace;font-size:2rem;
                      font-weight:800;background:linear-gradient(135deg,
                      {C['accent']},{C['purple']});
                      -webkit-background-clip:text;
                      -webkit-text-fill-color:transparent;">{symbol}</div>
          <div style="color:{C['muted']};font-size:0.85rem;margin-top:3px;">
            {info.get('name','')}
            {'&nbsp;·&nbsp;' + info.get('sector','') if info.get('sector','—') != '—' else ''}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:2.4rem;font-weight:800;
                      font-family:'Space Mono',monospace;color:{C['text']};">
            ${last:,.2f}
          </div>
          <div style="color:{chg_color};font-family:'Space Mono',monospace;
                      font-weight:700;font-size:1.1rem;">
            {arrow} {abs(change):.2f}%
          </div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
          <span class="status-badge {badge_cls}">{signal}</span>
          <div style="color:{C['muted']};font-size:0.7rem;
                      font-family:'Space Mono',monospace;">
            Güven: {pred_prob*100:.0f}%
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    _live_price_section(symbol)

    # ── 5 Metrik Kartı ────────────────────────────────────────────────────────
    c1,c2,c3,c4,c5 = st.columns(5)
    _card(c1, "📊 Piyasa Değeri",
          format_market_cap(info.get("market_cap")),
          color=C["accent"])
    _card(c2, "📈 RSI (14)", f"{rsi_v:.1f}",
          sub="🔴 Aşırı Alım" if rsi_v>70 else ("🟢 Aşırı Satım" if rsi_v<30 else "🟡 Normal"),
          color=C["red"] if rsi_v>70 else (C["green"] if rsi_v<30 else C["yellow"]))
    _card(c3, "⚡ MACD Hist", f"{macd_h:+.4f}",
          sub="🟢 Yükseliş" if macd_h>0 else "🔴 Düşüş",
          color=C["green"] if macd_h>0 else C["red"])
    _card(c4, "🎯 Model Güven", f"{pred_prob*100:.1f}%",
          sub="🟢 YUKARI" if pred_prob>0.5 else "🔴 AŞAĞI",
          color=C["green"] if pred_prob>0.5 else C["red"])
    with c4:
        with st.expander("Model Güven Açıklaması", expanded=False):
            st.write("Model güven skoru aşağıdaki şekilde üretilir ve yorumlanmalıdır:")
            st.write("1) Skorun kaynağı: Bu skor, Random Forest sınıflandırıcısının" \
                     "test setindeki en son örnek için hesapladığı " \
                     "sınıf 1 (yukarı) olasılığıdır. Kodda model train_random_forest() ile" \
                     "eğitilir ve model.predict_proba(X_test)[:, 1] kullanılarak elde edilir.")
            st.write("2) Kullanılan girdiler: Model, prepare_rf_data() ile hazırlanan 21 teknik gösterge" \
                     "özelliği üzerinden çalışır; bu özellikler StandardScaler ile ölçeklendirilir." )
            st.write("3) Sinyal hesaplama ile ilişkisi: Uygulamada model olasılığı compute_signal()" \
                     "fonksiyonunda skora katkı sağlar; kodda skora (pred_prob - 0.5) * 4" \
                     "ile ek bir ağırlık eklenir, dolayısıyla olasılık 0.5 etrafındaki sapmalar" \
                     "sinyal üzerinde orantılı etki yapar.")
            st.write("4) Yorum ve sınırlamalar: Bu olasılık bir kesinlik garantisi değildir;" \
                     "istatistiksel bir tahmindir ve modelin geçmiş test verisindeki performansına" \
                     "dayanmaktadır. Değerlendirilen metrikler (örneğin doğruluk ve AUC)" \
                     "evaluate_model fonksiyonunda hesaplanır ancak tek bir örnek için verilen" \
                     "olasılık gerçek dünya belirsizliklerini tamamen yansıtmaz.")
            st.write("5) Düşük skor uyarısı: Skorun 50% altı olması modelin belirsiz veya zayıf" \
                     "bir öngörü verdiğini gösterebilir; bu durumda ek göstergelere, haber" \
                     "duygu analizine veya manuel değerlendirmeye başvurulması önerilir.")
    _card(c5, "📰 Haber Duygu", sent_agg["overall"],
          sub=f"✅{sent_agg['positive']}  ❌{sent_agg['negative']}",
          color=C["green"] if sent_agg["overall"]=="Pozitif"
               else (C["red"] if sent_agg["overall"]=="Negatif" else C["yellow"]))

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Sekmeler ──────────────────────────────────────────────────────────────
    tab1,tab2,tab3,tab4 = st.tabs([
        "📊  Fiyat & Göstergeler",
        "🔬  Model Analizi",
        "📰  Haber Duygu",
        "📉  Korelasyon",
    ])
    with tab1:
        _price_chart(df, symbol)
        _indicator_charts(df)
    with tab2:
        _model_analysis(df)
    with tab3:
        _news_section(news, sent_agg)
    with tab4:
        _corr_chart(df)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    _pdf_export_button(symbol, info, df, last, change, rsi_v, macd_h,
                        pred_prob, signal, sent_agg, news, last_update)

    # Veri kaynagi bilgisi
    st.markdown(f"""
    <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid {C['border']};
                color:{C['muted']};font-size:0.75rem;font-family:'Space Mono',monospace;">
      Veri kaynagi: Yahoo Finance | Son guncelleme: {last_update.strftime('%Y-%m-%d %H:%M:%S')}
    </div>""", unsafe_allow_html=True)


# ── Yasal uyari notu ──────────────────────────────────────────────────────────
def _disclaimer_note():
    note_col, link_col = st.columns([5, 1])
    with note_col:
        st.markdown(f"""
        <div style="color:{C['muted']};font-size:0.75rem;
                    font-family:'Space Mono',monospace;padding-top:0.4rem;">
          Bu platform egitim ve bilgilendirme amaclidir, yatirim tavsiyesi degildir.
        </div>""", unsafe_allow_html=True)
    with link_col:
        if st.button("Yasal Uyari", key="dashboard_disclaimer_link", use_container_width=True):
            st.session_state["nav_redirect"] = "Yasal Uyari"
            st.rerun()


# ── Canli Fiyat Takibi ─────────────────────────────────────────────────────────
def _live_price_section(symbol):
    tcol, scol = st.columns([1, 3])
    with tcol:
        auto_refresh = st.toggle(
            "Otomatik Yenileme",
            value=st.session_state.get("auto_refresh_enabled", False),
            key="auto_refresh_enabled",
            help="Acildiginda fiyat, RSI ve MACD degerleri 30 saniyede bir "
                 "otomatik olarak yenilenir. Model tahmini ve haber analizi "
                 "bu yenilemeye dahil degildir, bu yuzden yeniden egitim "
                 "yapilmaz.",
        )
    refresh_interval = 30 if auto_refresh else None

    @st.fragment(run_every=refresh_interval)
    def _live_refresh():
        try:
            live_df = fetch_stock_data(symbol, period="6mo", interval="1d")
        except Exception:
            live_df = None

        if live_df is None or live_df.empty or len(live_df) < 2:
            st.markdown(f"""
            <div style="color:{C['muted']};font-size:0.78rem;
                        font-family:'Space Mono',monospace;padding:0.5rem 0;">
              Canli veri alinamadi.
            </div>""", unsafe_allow_html=True)
            return

        live_last   = float(live_df["Close"].iloc[-1])
        live_prev   = float(live_df["Close"].iloc[-2])
        live_change = (live_last - live_prev) / live_prev * 100
        live_rsi    = float(live_df["RSI"].iloc[-1])
        live_macd   = float(live_df["MACD_Hist"].iloc[-1])
        chg_color   = C["green"] if live_change >= 0 else C["red"]
        now_str     = datetime.now().strftime("%H:%M:%S")

        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {C['border']};
                    border-radius:10px;padding:0.65rem 1.2rem;margin-bottom:0.8rem;
                    display:flex;flex-wrap:wrap;gap:1.8rem;align-items:center;
                    font-family:'Space Mono',monospace;">
          <div style="color:{C['text']};font-size:1rem;font-weight:700;">
            ${live_last:,.2f}
            <span style="color:{chg_color};font-size:0.82rem;font-weight:700;">
              {'+' if live_change >= 0 else ''}{live_change:.2f}%
            </span>
          </div>
          <div style="color:{C['muted']};font-size:0.78rem;">
            RSI <span style="color:{C['text']};">{live_rsi:.1f}</span>
          </div>
          <div style="color:{C['muted']};font-size:0.78rem;">
            MACD Hist <span style="color:{C['text']};">{live_macd:+.4f}</span>
          </div>
          <div style="color:{C['muted']};font-size:0.72rem;margin-left:auto;">
            Son guncelleme: {now_str}
          </div>
        </div>""", unsafe_allow_html=True)

    with scol:
        _live_refresh()


# ── PDF Rapor Disa Aktarma ─────────────────────────────────────────────────────
def _pdf_export_button(symbol, info, df, last, change, rsi_v, macd_h,
                        pred_prob, signal, sent_agg, news, last_update):
    try:
        pdf_bytes = generate_pdf_report(
            symbol, info, df, last, change, rsi_v, macd_h,
            pred_prob, signal, sent_agg, news, last_update,
        )
        st.download_button(
            "📄  PDF RAPOR İNDİR",
            data=pdf_bytes,
            file_name=f"{symbol}_StockAI_Rapor_{last_update.strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception:
        st.warning("PDF rapor olusturulamadi. Lutfen tekrar deneyin.")


# ── Kart helper ───────────────────────────────────────────────────────────────
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


# ── Fiyat Grafiği ─────────────────────────────────────────────────────────────
def _price_chart(df, symbol):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.74, 0.26], vertical_spacing=0.04)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="OHLC",
        increasing=dict(line_color=C["green"], fillcolor=rgba(C["green"], 0.82),
                         line=dict(width=1)),
        decreasing=dict(line_color=C["red"],   fillcolor=rgba(C["red"], 0.82),
                         line=dict(width=1)),
    ), row=1, col=1)

    for ma, col, w in [("MA20", C["accent"], LINE_MAIN),
                        ("MA50", C["yellow"], LINE_THIN),
                        ("MA10", C["purple"], LINE_HAIR)]:
        fig.add_trace(go.Scatter(x=df.index, y=df[ma], name=ma,
            line=dict(color=col, width=w),
            hovertemplate=f"{ma}: %{{y:.2f}}<extra></extra>"), row=1, col=1)

    # Bollinger Bands — hover kutusunu kalabalıklaştırmasın diye hover kapalı
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"],
        line=dict(color=rgba(C["text"], 0.10), width=1, dash="dot"),
        showlegend=False, name="BB Üst", hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"],
        fill="tonexty", fillcolor=rgba(C["accent"], 0.045),
        line=dict(color=rgba(C["text"], 0.10), width=1, dash="dot"),
        showlegend=False, name="BB Alt", hoverinfo="skip"), row=1, col=1)

    # Hacim — hafif gradyanlı derinlik
    vcols = [rgba(C["green"], 0.7) if df["Close"].iloc[i] >= df["Open"].iloc[i]
             else rgba(C["red"], 0.7) for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"],
        marker=dict(color=vcols, line_width=0), name="Hacim",
        hovertemplate="Hacim: %{y:,.0f}<extra></extra>"), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(color=C["text"], family=FONT_FAMILY, size=10.5),
        margin=dict(l=55, r=24, t=56, b=62),
        title=dict(text=f"<b>{symbol}</b> — Candlestick + Bollinger Bands",
                   font=dict(size=TITLE_SIZE, color=C["text"]), x=0.01, xanchor="left"),
        xaxis_rangeslider_visible=False,
        height=560,
        hovermode="x unified",
        dragmode="zoom",
        xaxis_rangeselector=dict(
            buttons=list([
                dict(count=1, label="1A", step="month"),
                dict(count=3, label="3A", step="month"),
                dict(count=6, label="6A", step="month"),
                dict(step="year", label="1Y"),
                dict(step="all", label="Tümü")
            ]),
            bgcolor=C["s2"],
            font=dict(color=C["muted"], size=10.5, family=FONT_FAMILY),
            activecolor=C["accent"],
            y=1.10,
        ),
        legend=bottom_legend(y=-0.16),
        hoverlabel=hover_style(),
    )
    fig.update_xaxes(**base_axis())
    fig.update_yaxes(**base_axis())
    fig.update_yaxes(title_text="Fiyat (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Hacim",       row=2, col=1)

    st.plotly_chart(fig, use_container_width=True,
                     config=modebar_config(f"{symbol}_chart"))


# ── RSI + MACD ────────────────────────────────────────────────────────────────
def _indicator_charts(df):
    c1, c2 = st.columns(2)
    chart_config = modebar_config("indicators")

    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
            line=dict(color=C["accent"], width=LINE_REG),
            fill="tozeroy", fillgradient=area_fillgradient(C["accent"], 0.20, 0.0),
            hovertemplate="RSI: %{y:.1f}<extra></extra>"))
        fig.add_hline(y=70, line_dash="dash", line_width=1, line_color=C["red"],   opacity=0.45)
        fig.add_hline(y=30, line_dash="dash", line_width=1, line_color=C["green"], opacity=0.45)
        fig.add_hrect(y0=30, y1=70, fillcolor=rgba(C["accent"], 0.03), line_width=0)
        fig.update_layout(**pl("<b>RSI</b> (14)", height=320, show_legend=False,
                                margin=dict(l=42, r=20, t=52, b=30)),
                          hovermode="x", dragmode="zoom")
        st.plotly_chart(fig, use_container_width=True, config=chart_config)

    with c2:
        fig = go.Figure()
        hcols = [rgba(C["green"], 0.75) if v >= 0 else rgba(C["red"], 0.75) for v in df["MACD_Hist"]]
        fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"],
            marker=dict(color=hcols, line_width=0), name="Histogram",
            hovertemplate="Histogram: %{y:.4f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],
            line=dict(color=C["accent"], width=LINE_REG), name="MACD",
            hovertemplate="MACD: %{y:.4f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"],
            line=dict(color=C["yellow"], width=LINE_THIN), name="Sinyal",
            hovertemplate="Sinyal: %{y:.4f}<extra></extra>"))
        fig.update_layout(**pl("<b>MACD</b>", height=320,
                                margin=dict(l=42, r=20, t=52, b=78),
                                legend=bottom_legend(y=-0.55)),
                          hovermode="x unified", dragmode="zoom")
        st.plotly_chart(fig, use_container_width=True, config=chart_config)


# ── Model Analizi ─────────────────────────────────────────────────────────────
def _model_analysis(df):
    with st.spinner("🧠  Random Forest eğitiliyor..."):
        X_train, X_test, y_train, y_test, scaler, feat_names = prepare_rf_data(df)
        model   = train_random_forest(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test, "rf")
        fi      = get_feature_importance(model, feat_names)

    if not metrics:
        st.warning("Model sonuçları üretilemedi."); return

    acc = metrics["accuracy"] * 100
    auc = metrics["auc"]
    rep = metrics["report"]

    # Metrik kartları
    mc1,mc2,mc3,mc4 = st.columns(4)
    _card(mc1,"🎯 Doğruluk",     f"{acc:.1f}%",
          color=C["green"] if acc>60 else C["yellow"])
    _card(mc2,"📐 AUC-ROC",      f"{auc:.3f}",
          color=C["green"] if auc>0.55 else C["yellow"])
    _card(mc3,"✅ Precision (↑)", f"{rep['1']['precision']:.3f}",
          sub="YUKARI sınıfı")
    _card(mc4,"🔁 Recall (↑)",   f"{rep['1']['recall']:.3f}",
          sub="YUKARI sınıfı")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    cl, cr = st.columns(2)

    # ── Feature Importance ────────────────────────────────────────────────────
    with cl:
        top   = fi[:14]
        names = [x[0] for x in top]
        vals  = [x[1] for x in top]

        fig = go.Figure(go.Bar(
            x=vals, y=names, orientation="h",
            marker=dict(
                color=vals,
                colorscale=[[0, C["purple"]], [0.5, C["accent"]], [1, C["green"]]],
                showscale=True,
                line_width=0,
                colorbar=dict(title=dict(text="Önem", font=dict(color=C["muted"], size=AXIS_TITLE)),
                              tickfont=dict(color=C["muted"], size=TICK_SIZE), thickness=12, outlinewidth=0),
            ),
            hovertemplate="<b>%{y}</b><br>Önem: %{x:.4f}<extra></extra>",
        ))
        # update_layout — yaxis'i direkt ver, pl() kullanma
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=PLOT_BG,
            font=dict(color=C["text"], family=FONT_FAMILY, size=TICK_SIZE),
            margin=dict(l=10, r=16, t=52, b=20),
            title=dict(text="<b>Feature Importance</b> — Top 14",
                       font=dict(size=TITLE_SIZE, color=C["text"]), x=0.01, xanchor="left"),
            height=430,
            hovermode="closest",
            dragmode="zoom",
            showlegend=False,
            xaxis=base_axis(),
            yaxis=dict(autorange="reversed", showgrid=False, zeroline=False,
                       tickfont=dict(size=TICK_SIZE, color=C["muted"], family=FONT_FAMILY)),
            hoverlabel=hover_style(),
        )
        chart_config = modebar_config("feature_importance")
        st.plotly_chart(fig, use_container_width=True, config=chart_config)

    # ── ROC Eğrisi ────────────────────────────────────────────────────────────
    with cr:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=metrics["roc_fpr"], y=metrics["roc_tpr"], mode="lines",
            name=f"RF  AUC = {auc:.3f}",
            line=dict(color=C["accent"], width=LINE_MAIN),
            fill="tozeroy", fillgradient=area_fillgradient(C["accent"], 0.22, 0.0),
            hovertemplate="FPR: %{x:.2f}<br>TPR: %{y:.2f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=[0,1], y=[0,1], mode="lines",
            line=dict(color=C["muted"], dash="dash", width=LINE_HAIR),
            name="Rastgele (0.5)", hoverinfo="skip"))
        fig.update_layout(**pl("<b>ROC Eğrisi</b>", height=430),
                          hovermode="closest", dragmode="zoom")
        st.plotly_chart(fig, use_container_width=True, config=chart_config)

    # ── Confusion Matrix ──────────────────────────────────────────────────────
    cm     = metrics["confusion_matrix"]
    labels = ["AŞAĞI (0)", "YUKARI (1)"]
    fig = go.Figure(go.Heatmap(
        z=cm, x=labels, y=labels,
        colorscale=[[0, C["s1"]], [0.5, "#312e81"], [1, C["accent"]]],
        text=[[str(v) for v in row] for row in cm],
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=22, color="white"),
        showscale=False,
        xgap=3, ygap=3,
        hovertemplate="Gerçek: %{y}<br>Tahmin: %{x}<br>Sayı: %{z}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(color=C["text"], family=FONT_FAMILY, size=TICK_SIZE),
        margin=dict(l=10, r=16, t=52, b=20),
        title=dict(text="<b>Confusion Matrix</b>",
                   font=dict(size=TITLE_SIZE, color=C["text"]), x=0.01, xanchor="left"),
        height=310,
        hovermode="closest",
        dragmode="zoom",
        showlegend=False,
        xaxis=dict(title=dict(text="Tahmin", font=dict(size=AXIS_TITLE, color=C["muted"])),
                    showgrid=False, tickfont=dict(size=TICK_SIZE, color=C["muted"])),
        yaxis=dict(title=dict(text="Gerçek", font=dict(size=AXIS_TITLE, color=C["muted"])),
                    showgrid=False, tickfont=dict(size=TICK_SIZE, color=C["muted"])),
        hoverlabel=hover_style(),
    )
    st.plotly_chart(fig, use_container_width=True, config=chart_config)

    # ── Sınıflandırma Raporu tablosu ──────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-radius:10px;padding:1.1rem 1.5rem;margin-top:4px;">
      <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:0.8rem;">
        Sınıflandırma Raporu
      </div>
      <table style="width:100%;border-collapse:collapse;
                    font-family:'Space Mono',monospace;font-size:0.82rem;">
        <tr style="color:{C['muted']};border-bottom:1px solid {C['border']};">
          <td style="padding:6px 0">Sınıf</td>
          <td style="padding:6px">Precision</td>
          <td style="padding:6px">Recall</td>
          <td style="padding:6px">F1-Score</td>
          <td style="padding:6px">Support</td>
        </tr>
        <tr style="color:{C['red']};">
          <td style="padding:6px 0">↓ AŞAĞI (0)</td>
          <td style="padding:6px">{rep['0']['precision']:.3f}</td>
          <td style="padding:6px">{rep['0']['recall']:.3f}</td>
          <td style="padding:6px">{rep['0']['f1-score']:.3f}</td>
          <td style="padding:6px">{int(rep['0']['support'])}</td>
        </tr>
        <tr style="color:{C['green']};">
          <td style="padding:6px 0">↑ YUKARI (1)</td>
          <td style="padding:6px">{rep['1']['precision']:.3f}</td>
          <td style="padding:6px">{rep['1']['recall']:.3f}</td>
          <td style="padding:6px">{rep['1']['f1-score']:.3f}</td>
          <td style="padding:6px">{int(rep['1']['support'])}</td>
        </tr>
        <tr style="color:{C['accent']};border-top:1px solid {C['border']};">
          <td style="padding:6px 0">Genel Doğruluk</td>
          <td style="padding:6px"></td><td></td>
          <td style="padding:6px"><b>{acc:.1f}%</b></td>
          <td style="padding:6px">{int(rep['macro avg']['support'])}</td>
        </tr>
      </table>
    </div>""", unsafe_allow_html=True)


# ── Haberler ──────────────────────────────────────────────────────────────────
def _news_section(news, agg):
    c1,c2,c3,c4 = st.columns(4)
    _card(c1,"📊 Ort. Skor",  f"{agg['avg_score']:+.2f}")
    _card(c2,"✅ Pozitif",    str(agg["positive"]), color=C["green"])
    _card(c3,"❌ Negatif",    str(agg["negative"]), color=C["red"])
    _card(c4,"➖ Nötr",       str(agg["neutral"]),  color=C["yellow"])

    # Gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=agg["avg_score"] * 100,
        title={"text": "Genel Duygu Skoru",
               "font": {"color": C["muted"], "family": FONT_FAMILY, "size": TITLE_SIZE}},
        number={"font": {"color": C["text"], "family": FONT_FAMILY, "size": 24}},
        gauge={
            "axis": {"range": [-100, 100],
                     "tickcolor": C["muted"],
                     "tickfont": {"color": C["muted"], "size": TICK_SIZE}},
            "bar": {"color": C["accent"], "thickness": 0.18},
            "bgcolor": C["s2"],
            "borderwidth": 1, "bordercolor": rgba(C["muted"], 0.28),
            "steps": [
                {"range": [-100, -10], "color": rgba(C["red"], 0.12)},
                {"range": [-10, 10],   "color": rgba(C["yellow"], 0.07)},
                {"range": [10, 100],   "color": rgba(C["green"], 0.12)},
            ],
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=C["text"], family=FONT_FAMILY),
                      height=220, margin=dict(l=20, r=20, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

    for n in news:
        lbl   = n["sentiment"]["label"]
        clr   = {"Pozitif":C["green"],"Negatif":C["red"],"Nötr":C["yellow"]}[lbl]
        score = n["sentiment"]["score"]
        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {C['border']};
                    border-left:3px solid {clr};border-radius:10px;
                    padding:0.85rem 1.2rem;margin-bottom:0.55rem;">
          <div style="display:flex;justify-content:space-between;
                      align-items:flex-start;gap:1rem;">
            <div style="flex:1;">
              <div style="font-weight:600;margin-bottom:4px;color:{C['text']};">
                {n['title']}
              </div>
              <div style="color:{C['muted']};font-size:0.75rem;
                          font-family:'Space Mono',monospace;">
                {n['source']} &nbsp;·&nbsp; {n['published']}
              </div>
            </div>
            <div style="text-align:center;min-width:72px;">
              <div style="color:{clr};font-weight:700;
                          font-family:'Space Mono',monospace;">{lbl}</div>
              <div style="color:{clr};font-size:0.78rem;
                          font-family:'Space Mono',monospace;">{score:+.2f}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)


# ── Korelasyon ────────────────────────────────────────────────────────────────
def _corr_chart(df):
    cols = ["Close","RSI","MACD","BB_Pos","Volatility",
            "Momentum","Return","Volume_Ratio","ATR","Stoch_K"]
    corr = df[cols].corr()

    fig = px.imshow(
        corr, text_auto=".2f",
        color_continuous_scale=[[0, C["red"]], [0.5, C["s1"]], [1, C["green"]]],
        zmin=-1, zmax=1,
        labels=dict(color="Korelasyon"),
    )
    fig.update_traces(
        textfont=dict(size=10, color="white"),
        xgap=2, ygap=2,
        hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>r = %{z:.3f}<extra></extra>",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(color=C["text"], family=FONT_FAMILY, size=TICK_SIZE),
        margin=dict(l=10, r=16, t=52, b=10),
        title=dict(text="<b>Özellik Korelasyon Matrisi</b>",
                   font=dict(size=TITLE_SIZE, color=C["text"]), x=0.01, xanchor="left"),
        height=490,
        xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(size=TICK_SIZE, color=C["muted"])),
        yaxis=dict(showgrid=False, tickfont=dict(size=TICK_SIZE, color=C["muted"])),
        coloraxis_colorbar=dict(
            tickfont=dict(color=C["muted"], size=TICK_SIZE),
            title=dict(text="r", font=dict(color=C["muted"])),
            thickness=12, outlinewidth=0,
        ),
        hoverlabel=hover_style(),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Yüksek korelasyon yorumu
    high = [(corr.columns[i], corr.columns[j], corr.iloc[i,j])
            for i in range(len(corr))
            for j in range(i+1, len(corr))
            if abs(corr.iloc[i,j]) > 0.70]
    if high:
        rows = "".join(
            f'<tr><td style="padding:4px 8px;color:{C["green"] if v>0 else C["red"]}">'
            f'{"+" if v>0 else ""}{v:.2f}</td>'
            f'<td style="padding:4px 8px;color:{C["text"]}">{a}</td>'
            f'<td style="padding:4px 8px;color:{C["muted"]}">↔</td>'
            f'<td style="padding:4px 8px;color:{C["text"]}">{b}</td></tr>'
            for a,b,v in high[:6]
        )
        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {C['border']};
                    border-radius:10px;padding:1rem 1.2rem;margin-top:6px;">
          <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                      text-transform:uppercase;margin-bottom:0.6rem;">
            Yüksek Korelasyonlar (|r| &gt; 0.70)
          </div>
          <table style="font-family:'Space Mono',monospace;font-size:0.8rem;">
            {rows}
          </table>
        </div>""", unsafe_allow_html=True)


# ── Hızlı tahmin ──────────────────────────────────────────────────────────────
def _quick_predict(df):
    try:
        X_train,X_test,y_train,_,_,_ = prepare_rf_data(df)
        m = train_random_forest(X_train, y_train, n_estimators=80)
        return float(m.predict_proba(X_test[-1:])[0][1])
    except:
        return 0.5


# ── Karşılama ─────────────────────────────────────────────────────────────────
def _welcome():
    items = [("🤖","LSTM + RF\nModelleri"),("📊","21 Teknik\nGösterge"),
             ("📰","Haber\nDuygu NLP"),("🌍","BIST + ABD\nPiyasaları"),
             ("📈","Backtest\nSimülasyon")]
    cards = "".join(
        f'<div style="background:{C["s2"]};border:1px solid {C["border"]};'
        f'border-radius:12px;padding:1.1rem 1.4rem;min-width:110px;">'
        f'<div style="font-size:1.8rem;">{ic}</div>'
        f'<div style="font-family:Space Mono,monospace;font-size:0.72rem;'
        f'margin-top:0.5rem;color:{C["muted"]};white-space:pre-line;">{tx}</div>'
        f'</div>' for ic,tx in items
    )
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem;">
      <div style="font-size:3.5rem;margin-bottom:1rem;">📈</div>
      <h2 style="font-family:'Space Mono',monospace;
                 background:linear-gradient(135deg,{C['accent']},{C['purple']});
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 font-size:2rem;">StockAI Pro</h2>
      <p style="color:{C['muted']};max-width:480px;margin:0.8rem auto 2rem;
                line-height:1.8;font-size:0.95rem;">
        Sol panelden bir <b style="color:{C['accent']}">hisse senedi</b> seçin
        ve <b style="color:{C['accent']}">ANALİZİ BAŞLAT</b> butonuna tıklayın.
      </p>
      <div style="display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;">
        {cards}
      </div>
    </div>""", unsafe_allow_html=True)
