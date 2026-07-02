"""
pages/dashboard.py  –  Ana Dashboard  (v3 – yaxis çakışması yok)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from utils.data_utils import (fetch_stock_data, get_ticker_info,
    format_market_cap, compute_signal, prepare_rf_data)
from utils.sentiment_utils import fetch_news, aggregate_sentiment
from utils.model_utils import train_random_forest, evaluate_model, get_feature_importance

# ────────────────────────────────────────────────────────────────────────────
C = {
    "bg":     "#0a0e1a",
    "s1":     "#111827",
    "s2":     "#1a2235",
    "border": "#1e2d45",
    "accent": "#00d4ff",
    "purple": "#7c3aed",
    "green":  "#10b981",
    "red":    "#ef4444",
    "yellow": "#f59e0b",
    "text":   "#e2e8f0",
    "muted":  "#64748b",
}

def pl(title="", height=350, **extra):
    """
    Güvenli plot layout üretici.
    extra içinde yaxis varsa base'i ezer → çakışma olmaz.
    """
    base = dict(
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(17,24,39,0.7)",
        font          = dict(color=C["text"], family="Space Mono, monospace"),
        margin        = dict(l=10, r=10, t=48, b=10),
        title         = dict(text=title,
                             font=dict(size=14, color=C["text"]),
                             x=0.01),
        xaxis = dict(gridcolor=C["border"], showgrid=True,
                     gridwidth=0.5, zeroline=False),
        yaxis = dict(gridcolor=C["border"], showgrid=True,
                     gridwidth=0.5, zeroline=False),
        legend = dict(bgcolor="rgba(26,34,53,0.85)",
                      bordercolor=C["border"], borderwidth=1,
                      font=dict(size=11)),
        hoverlabel = dict(bgcolor=C["s2"], font_color=C["text"],
                          font_family="Space Mono"),
        height = height,
    )
    # extra anahtarlarını tek tek merge et
    # eğer extra'da yaxis/xaxis varsa, base'deki tamamen değiştirilir
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = {**base[k], **v}   # dict ise birleştir
        else:
            base[k] = v                   # değilse üzerine yaz
    return base

# ════════════════════════════════════════════════════════════════════════════
def show_dashboard(symbol, period, window_size, run_analysis, interval="1d"):
    st.markdown('<p class="section-title">// ANA DASHBOARD</p>',
                unsafe_allow_html=True)
    if not run_analysis:
        _welcome(); return

    with st.spinner(f"📡  {symbol} verisi çekiliyor..."):
        df = fetch_stock_data(symbol, period, interval=interval)
    if df.empty:
        st.error(f"❌  {symbol} için veri alınamadı."); return

    info     = get_ticker_info(symbol)
    news     = fetch_news(symbol)
    sent_agg = aggregate_sentiment(news)

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
                        row_heights=[0.72, 0.28], vertical_spacing=0.03)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="OHLC",
        increasing=dict(line_color=C["green"], fillcolor=C["green"]),
        decreasing=dict(line_color=C["red"],   fillcolor=C["red"]),
    ), row=1, col=1)

    for ma, col, w in [("MA20",C["accent"],1.6),
                        ("MA50",C["yellow"],1.6),
                        ("MA10",C["purple"],1.0)]:
        fig.add_trace(go.Scatter(x=df.index, y=df[ma], name=ma,
            line=dict(color=col, width=w)), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"],
        line=dict(color="rgba(255,255,255,0.10)", width=1, dash="dot"),
        showlegend=False, name="BB Üst"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"],
        fill="tonexty", fillcolor="rgba(0,212,255,0.04)",
        line=dict(color="rgba(255,255,255,0.10)", width=1, dash="dot"),
        showlegend=False, name="BB Alt"), row=1, col=1)

    # Hacim
    vcols = [C["green"] if df["Close"].iloc[i] >= df["Open"].iloc[i]
             else C["red"] for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"],
        marker_color=vcols, opacity=0.6, name="Hacim"), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.7)",
        font=dict(color=C["text"], family="Space Mono, monospace"),
        margin=dict(l=10, r=10, t=48, b=10),
        title=dict(text=f"<b>{symbol}</b> — Candlestick + Bollinger Bands",
                   font=dict(size=14, color=C["text"]), x=0.01),
        xaxis_rangeslider_visible=False,
        height=560,
        legend=dict(orientation="h", y=1.04, x=0,
                    bgcolor="rgba(26,34,53,0.85)",
                    bordercolor=C["border"], borderwidth=1),
        hoverlabel=dict(bgcolor=C["s2"], font_color=C["text"],
                        font_family="Space Mono"),
    )
    fig.update_xaxes(gridcolor=C["border"], showgrid=True, gridwidth=0.5)
    fig.update_yaxes(gridcolor=C["border"], showgrid=True, gridwidth=0.5, zeroline=False)
    fig.update_yaxes(title_text="Fiyat (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Hacim",       row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)


# ── RSI + MACD ────────────────────────────────────────────────────────────────
def _indicator_charts(df):
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
            line=dict(color=C["accent"], width=2),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.05)"))
        fig.add_hline(y=70, line_dash="dash", line_color=C["red"],   opacity=0.5)
        fig.add_hline(y=30, line_dash="dash", line_color=C["green"], opacity=0.5)
        fig.add_hrect(y0=30, y1=70, fillcolor="rgba(0,212,255,0.03)")
        fig.update_layout(**pl("<b>RSI</b> (14)", height=270))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure()
        hcols = [C["green"] if v >= 0 else C["red"] for v in df["MACD_Hist"]]
        fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"],
            marker_color=hcols, opacity=0.8, name="Histogram"))
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],
            line=dict(color=C["accent"], width=1.8), name="MACD"))
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"],
            line=dict(color=C["yellow"], width=1.5), name="Sinyal"))
        fig.update_layout(**pl("<b>MACD</b>", height=270))
        st.plotly_chart(fig, use_container_width=True)


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
                colorscale=[[0,"#7c3aed"],[0.5,"#00d4ff"],[1,"#10b981"]],
                showscale=True,
                colorbar=dict(title="Önem",
                              tickfont=dict(color=C["text"]),
                              title_font=dict(color=C["text"])),
            ),
            hovertemplate="<b>%{y}</b><br>Önem: %{x:.4f}<extra></extra>",
        ))
        # update_layout — yaxis'i direkt ver, pl() kullanma
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,24,39,0.7)",
            font=dict(color=C["text"], family="Space Mono, monospace"),
            margin=dict(l=10, r=10, t=48, b=10),
            title=dict(text="<b>Feature Importance</b> — Top 14",
                       font=dict(size=14, color=C["text"]), x=0.01),
            height=430,
            xaxis=dict(gridcolor=C["border"], showgrid=True,
                       gridwidth=0.5, zeroline=False),
            yaxis=dict(autorange="reversed",
                       gridcolor=C["border"], showgrid=False),
            hoverlabel=dict(bgcolor=C["s2"], font_color=C["text"],
                            font_family="Space Mono"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── ROC Eğrisi ────────────────────────────────────────────────────────────
    with cr:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=metrics["roc_fpr"], y=metrics["roc_tpr"], mode="lines",
            name=f"RF  AUC = {auc:.3f}",
            line=dict(color=C["accent"], width=2.5),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.07)",
        ))
        fig.add_trace(go.Scatter(
            x=[0,1], y=[0,1], mode="lines",
            line=dict(color=C["muted"], dash="dash", width=1),
            name="Rastgele (0.5)"))
        fig.update_layout(**pl("<b>ROC Eğrisi</b>", height=430))
        st.plotly_chart(fig, use_container_width=True)

    # ── Confusion Matrix ──────────────────────────────────────────────────────
    cm     = metrics["confusion_matrix"]
    labels = ["AŞAĞI (0)", "YUKARI (1)"]
    fig = go.Figure(go.Heatmap(
        z=cm, x=labels, y=labels,
        colorscale=[[0,C["s1"]],[0.5,"#312e81"],[1,C["accent"]]],
        text=[[str(v) for v in row] for row in cm],
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=24, color="white"),
        showscale=False,
        hovertemplate="Gerçek: %{y}<br>Tahmin: %{x}<br>Sayı: %{z}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.7)",
        font=dict(color=C["text"], family="Space Mono, monospace"),
        margin=dict(l=10, r=10, t=48, b=10),
        title=dict(text="<b>Confusion Matrix</b>",
                   font=dict(size=14, color=C["text"]), x=0.01),
        height=310,
        xaxis=dict(title="Tahmin", gridcolor=C["border"]),
        yaxis=dict(title="Gerçek", gridcolor=C["border"]),
        hoverlabel=dict(bgcolor=C["s2"], font_color=C["text"],
                        font_family="Space Mono"),
    )
    st.plotly_chart(fig, use_container_width=True)

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
        title={"text":"Genel Duygu Skoru",
               "font":{"color":C["text"],"family":"Space Mono","size":13}},
        number={"font":{"color":C["text"],"family":"Space Mono","size":24}},
        gauge={
            "axis":{"range":[-100,100],
                    "tickcolor":C["muted"],
                    "tickfont":{"color":C["muted"]}},
            "bar":{"color":C["accent"],"thickness":0.22},
            "bgcolor":C["s2"],
            "borderwidth":1,"bordercolor":C["border"],
            "steps":[
                {"range":[-100,-10],"color":"rgba(239,68,68,0.12)"},
                {"range":[-10,10],  "color":"rgba(245,158,11,0.07)"},
                {"range":[10,100],  "color":"rgba(16,185,129,0.12)"},
            ],
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=C["text"], family="Space Mono"),
                      height=220, margin=dict(l=20,r=20,t=50,b=10))
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
        color_continuous_scale=[[0,C["red"]],[0.5,C["s1"]],[1,C["green"]]],
        zmin=-1, zmax=1,
        labels=dict(color="Korelasyon"),
    )
    fig.update_traces(
        textfont=dict(size=10, color="white"),
        hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>r = %{z:.3f}<extra></extra>",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.7)",
        font=dict(color=C["text"], family="Space Mono, monospace"),
        margin=dict(l=10, r=10, t=48, b=10),
        title=dict(text="<b>Özellik Korelasyon Matrisi</b>",
                   font=dict(size=14, color=C["text"]), x=0.01),
        height=490,
        xaxis=dict(gridcolor=C["border"], tickangle=-35),
        yaxis=dict(gridcolor=C["border"]),
        coloraxis_colorbar=dict(
            tickfont=dict(color=C["text"]),
            title=dict(text="r", font=dict(color=C["text"])),
        ),
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
