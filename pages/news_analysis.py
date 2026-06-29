"""
pages/news_analysis.py  –  Haber Duygu Analizi Sayfası
Değerlendirme: NLP bileşeni (D-3 kapsamlı proje)
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# DÜZELTME: utils.news_utils değil utils.sentiment_utils
from utils.sentiment_utils import (fetch_news, aggregate_sentiment,
                                    analyze_sentiment_lexicon)

C = {"bg":"#0a0e1a","s1":"#111827","s2":"#1a2235","border":"#1e2d45",
     "accent":"#00d4ff","purple":"#7c3aed","green":"#10b981",
     "red":"#ef4444","yellow":"#f59e0b","text":"#e2e8f0","muted":"#64748b"}

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

# ════════════════════════════════════════════════════════════════════════════
def show_news_analysis(symbol):
    st.markdown('<p class="section-title">// HABER DUYGU ANALİZİ (NLP)</p>',
                unsafe_allow_html=True)

    # ── Açıklama ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-left:3px solid {C['purple']};border-radius:10px;
                padding:1rem 1.4rem;margin-bottom:1.2rem;font-size:0.85rem;
                color:{C['muted']};line-height:1.8;">
      <b style="color:{C['purple']}">NLP Bileşeni:</b>
      Finans odaklı kelime sözlüğü ile haber metinleri
      <b style="color:{C['text']}">Pozitif / Negatif / Nötr</b>
      olarak sınıflandırılır. Skor <b style="color:{C['text']}">−1.0</b> (çok negatif)
      ile <b style="color:{C['text']}">+1.0</b> (çok pozitif) arasındadır.
    </div>""", unsafe_allow_html=True)

    # ── Canlı Metin Analizi ───────────────────────────────────────────────────
    st.markdown(f"""
    <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                text-transform:uppercase;margin-bottom:0.5rem;">
      Metin Duygu Analizi (Canlı)
    </div>""", unsafe_allow_html=True)

    col_in, col_btn = st.columns([4, 1])
    with col_in:
        custom = st.text_area("",
            placeholder="Buraya bir haber başlığı yazın veya yapıştırın...",
            height=80, label_visibility="collapsed")
    with col_btn:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        analyze_clicked = st.button("🔍 ANALİZ ET", use_container_width=True)

    if analyze_clicked and custom.strip():
        r     = analyze_sentiment_lexicon(custom)
        lbl   = r["label"]
        score = r["score"]
        clr   = {"Pozitif":C["green"],"Negatif":C["red"],"Nötr":C["yellow"]}[lbl]
        pct   = abs(score) * 100

        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {clr};
                    border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      flex-wrap:wrap;gap:1rem;">
            <div>
              <div style="color:{clr};font-size:1.8rem;font-weight:800;
                          font-family:'Space Mono',monospace;">{lbl}</div>
              <div style="color:{C['muted']};font-size:0.82rem;margin-top:4px;">
                Pozitif kelime: <b style="color:{C['green']}">{r['pos']}</b> &nbsp;|&nbsp;
                Negatif kelime: <b style="color:{C['red']}">{r['neg']}</b>
              </div>
            </div>
            <div style="text-align:right;">
              <div style="color:{clr};font-size:2rem;font-weight:800;
                          font-family:'Space Mono',monospace;">{score:+.2f}</div>
              <div style="color:{C['muted']};font-size:0.75rem;">Duygu Skoru</div>
            </div>
          </div>
          <div style="background:{C['border']};border-radius:4px;height:6px;margin-top:1rem;">
            <div style="width:{pct:.0f}%;height:100%;border-radius:4px;
                        background:{clr};transition:width 0.4s;"></div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Hisse Haberleri ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                text-transform:uppercase;margin-bottom:0.8rem;">
      {symbol} — Son Haberler
    </div>""", unsafe_allow_html=True)

    with st.spinner(f"📰  {symbol} haberleri analiz ediliyor..."):
        news = fetch_news(symbol)
        agg  = aggregate_sentiment(news)

    # Özet metrikler
    c1,c2,c3,c4 = st.columns(4)
    _card(c1, "📊 Ort. Skor",  f"{agg['avg_score']:+.2f}",
          color=C["green"] if agg['avg_score']>0 else C["red"])
    _card(c2, "✅ Pozitif",    str(agg["positive"]), color=C["green"])
    _card(c3, "❌ Negatif",    str(agg["negative"]), color=C["red"])
    _card(c4, "➖ Nötr",       str(agg["neutral"]),  color=C["yellow"])

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    col_gauge, col_pie = st.columns(2)

    # Gauge
    with col_gauge:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=agg["avg_score"] * 100,
            title={"text":"Genel Duygu Skoru",
                   "font":{"color":C["text"],"family":"Space Mono","size":13}},
            number={"font":{"color":C["text"],"family":"Space Mono","size":24},
                    "suffix":""},
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
                          font=dict(color=C["text"],family="Space Mono"),
                          height=250, margin=dict(l=20,r=20,t=55,b=10))
        st.plotly_chart(fig, use_container_width=True)

    # Pasta grafiği
    with col_pie:
        fig = go.Figure(go.Pie(
            labels=["Pozitif","Negatif","Nötr"],
            values=[agg["positive"], agg["negative"], agg["neutral"]],
            hole=0.58,
            marker=dict(colors=[C["green"],C["red"],C["yellow"]],
                        line=dict(color=C["bg"],width=2)),
            textfont=dict(color="white", family="Space Mono"),
            hovertemplate="<b>%{label}</b><br>%{value} haber (%{percent})<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>{agg['overall']}</b>",
                           x=0.5, y=0.5, font_size=16,
                           font_color={"Pozitif":C["green"],
                                       "Negatif":C["red"],
                                       "Nötr":C["yellow"]}[agg["overall"]],
                           showarrow=False)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                          font=dict(color=C["text"],family="Space Mono"),
                          title=dict(text="<b>Duygu Dağılımı</b>",
                                     font=dict(size=13,color=C["text"]),x=0.01),
                          height=250, margin=dict(l=10,r=10,t=45,b=10),
                          legend=dict(bgcolor="rgba(26,34,53,0.85)",
                                      bordercolor=C["border"],borderwidth=1))
        st.plotly_chart(fig, use_container_width=True)

    # ── Haber Kartları ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                text-transform:uppercase;margin:0.8rem 0;">
      Haber Detayları
    </div>""", unsafe_allow_html=True)

    for i, n in enumerate(news):
        lbl   = n["sentiment"]["label"]
        clr   = {"Pozitif":C["green"],"Negatif":C["red"],"Nötr":C["yellow"]}[lbl]
        score = n["sentiment"]["score"]
        pct   = abs(score)*100

        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {C['border']};
                    border-left:3px solid {clr};border-radius:10px;
                    padding:0.9rem 1.2rem;margin-bottom:0.55rem;">
          <div style="display:flex;justify-content:space-between;
                      align-items:flex-start;gap:1rem;">
            <div style="flex:1;">
              <div style="font-weight:600;margin-bottom:4px;color:{C['text']};">
                {n['title']}
              </div>
              <div style="color:{C['muted']};font-size:0.75rem;
                          font-family:'Space Mono',monospace;">
                📰 {n['source']} &nbsp;·&nbsp; 📅 {n['published']}
              </div>
              <div style="background:{C['border']};border-radius:3px;
                          height:4px;margin-top:8px;width:100%;">
                <div style="width:{pct:.0f}%;height:100%;border-radius:3px;
                            background:{clr};"></div>
              </div>
            </div>
            <div style="text-align:center;min-width:72px;">
              <div style="color:{clr};font-weight:700;font-size:0.9rem;
                          font-family:'Space Mono',monospace;">{lbl}</div>
              <div style="color:{clr};font-size:0.8rem;
                          font-family:'Space Mono',monospace;">{score:+.2f}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
