"""
pages/model_training.py  –  Model Eğitim Sayfası
Değerlendirme: %30 Model geliştirme ve eğitim süreci
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

from utils.data_utils import fetch_stock_data, prepare_rf_data, prepare_lstm_data
from utils.model_utils import (train_random_forest, evaluate_model,
                                get_feature_importance, train_lstm)

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

def _base_layout(title="", height=350, **extra):
    """Güvenli layout — yaxis çakışması yok."""
    d = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.7)",
        font=dict(color=C["text"], family="Space Mono, monospace"),
        margin=dict(l=10, r=10, t=48, b=10),
        title=dict(text=title, font=dict(size=14, color=C["text"]), x=0.01),
        xaxis=dict(gridcolor=C["border"], showgrid=True, gridwidth=0.5, zeroline=False),
        yaxis=dict(gridcolor=C["border"], showgrid=True, gridwidth=0.5, zeroline=False),
        legend=dict(bgcolor="rgba(26,34,53,0.85)", bordercolor=C["border"], borderwidth=1),
        hoverlabel=dict(bgcolor=C["s2"], font_color=C["text"], font_family="Space Mono"),
        height=height,
    )
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            d[k] = {**d[k], **v}
        else:
            d[k] = v
    return d

# ════════════════════════════════════════════════════════════════════════════
def show_model_training(symbol, period, window_size, interval="1d"):
    st.markdown('<p class="section-title">// MODEL EĞİTİMİ & DEĞERLENDİRME</p>',
                unsafe_allow_html=True)

    # ── Açıklama kutusu ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-left:3px solid {C['accent']};border-radius:10px;
                padding:1rem 1.4rem;margin-bottom:1.2rem;font-size:0.85rem;
                color:{C['muted']};line-height:1.8;">
      <b style="color:{C['accent']}">Adım 3 — Model Geliştirme:</b>
      Veri <b style="color:{C['text']}">%80 eğitim / %20 test</b> olarak ayrılır.
      Random Forest ve isteğe bağlı LSTM modeli eğitilir, karşılaştırılır.
      Hiperparametreler (ağaç sayısı, derinlik) ayarlanabilir.
    </div>""", unsafe_allow_html=True)

    # ── Kontroller ───────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        model_choice = st.selectbox("🤖 Model Seç", [
            "Random Forest",
            "Gradient Boosting",
            "LSTM (Derin Öğrenme)",
        ])
    with c2:
        n_est = st.slider("Ağaç Sayısı", 50, 500, 200, 50)
    with c3:
        max_depth = st.slider("Max Derinlik", 4, 20, 10, 2)

    if not st.button("🚀  MODELİ EĞİT", use_container_width=True):
        st.info("ℹ️  Model seçin ve MODELİ EĞİT butonuna tıklayın.")
        return

    # ── Veri çek ─────────────────────────────────────────────────────────────
    try:
        with st.spinner(f"Veri çekiliyor..."):
            df = fetch_stock_data(symbol, period, interval=interval)
        if df is None or df.empty:
            st.error(f"Bu sembol icin veri bulunamadi. Lutfen sembolu kontrol edin: {symbol}")
            return
    except Exception:
        st.error(f"Veri saglaycisina ulasilamadi. Lutfen birkac dakika sonra tekrar deneyin.")
        return
        st.error("❌  Veri alınamadı."); return

    if "LSTM" in model_choice:
        _train_show_lstm(df, window_size)
    else:
        _train_show_rf(df, n_est, max_depth, "Gradient" in model_choice)


# ── Random Forest / Gradient Boosting ────────────────────────────────────────
def _train_show_rf(df, n_est, max_depth, is_gb=False):
    label = "Gradient Boosting" if is_gb else "Random Forest"
    with st.spinner(f"🌲  {label} eğitiliyor..."):
        X_train, X_test, y_train, y_test, scaler, feat_names = prepare_rf_data(df)

        if is_gb:
            from sklearn.ensemble import GradientBoostingClassifier
            model = GradientBoostingClassifier(
                n_estimators=150, learning_rate=0.05,
                max_depth=4, subsample=0.8, random_state=42)
            model.fit(X_train, y_train)
        else:
            model = train_random_forest(X_train, y_train,
                                        n_estimators=n_est, max_depth=max_depth)

        metrics = evaluate_model(model, X_test, y_test, "rf")
        fi      = get_feature_importance(model, feat_names)

    if not metrics:
        st.error("Model değerlendirilemedi."); return

    acc = metrics["accuracy"] * 100
    auc = metrics["auc"]
    rep = metrics["report"]

    st.success(f"✅  {label} eğitimi tamamlandı!  Doğruluk: **{acc:.2f}%**")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Metrikler
    mc1,mc2,mc3,mc4 = st.columns(4)
    _card(mc1, "🎯 Doğruluk",      f"{acc:.2f}%",
          color=C["green"] if acc>60 else C["yellow"])
    _card(mc2, "📐 AUC-ROC",       f"{auc:.4f}",
          color=C["green"] if auc>0.55 else C["yellow"])
    _card(mc3, "✅ Precision (↑)", f"{rep['1']['precision']:.3f}",
          sub="YUKARI sınıfı")
    _card(mc4, "🔁 Recall (↑)",    f"{rep['1']['recall']:.3f}",
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
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,24,39,0.7)",
            font=dict(color=C["text"], family="Space Mono, monospace"),
            margin=dict(l=10, r=10, t=48, b=10),
            title=dict(text=f"<b>Feature Importance</b> — {label}",
                       font=dict(size=14, color=C["text"]), x=0.01),
            height=430,
            xaxis=dict(gridcolor=C["border"], showgrid=True, gridwidth=0.5, zeroline=False),
            yaxis=dict(autorange="reversed", gridcolor=C["border"], showgrid=False),
            hoverlabel=dict(bgcolor=C["s2"], font_color=C["text"], font_family="Space Mono"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── ROC Eğrisi ────────────────────────────────────────────────────────────
    with cr:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=metrics["roc_fpr"], y=metrics["roc_tpr"], mode="lines",
            name=f"AUC = {auc:.3f}",
            line=dict(color=C["accent"], width=2.5),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.07)",
        ))
        fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines",
            line=dict(color=C["muted"], dash="dash", width=1),
            name="Rastgele (0.5)"))
        fig.update_layout(**_base_layout(
            f"<b>ROC Eğrisi</b> — {label}", height=430))
        st.plotly_chart(fig, use_container_width=True)

    # ── Confusion Matrix ──────────────────────────────────────────────────────
    cm     = metrics["confusion_matrix"]
    labels = ["AŞAĞI (0)", "YUKARI (1)"]
    fig = go.Figure(go.Heatmap(
        z=cm, x=labels, y=labels,
        colorscale=[[0,C["s1"]],[0.5,"#312e81"],[1,C["accent"]]],
        text=[[str(v) for v in row] for row in cm],
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=26, color="white"),
        showscale=False,
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
        yaxis=dict(title="Gerçek",  gridcolor=C["border"]),
        hoverlabel=dict(bgcolor=C["s2"], font_color=C["text"], font_family="Space Mono"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Rapor Tablosu ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-radius:10px;padding:1.1rem 1.5rem;margin-top:4px;">
      <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:0.8rem;">
        Sınıflandırma Raporu — {label}
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
          <td colspan="2"></td>
          <td style="padding:6px"><b>{acc:.1f}%</b></td>
          <td style="padding:6px">{int(rep['macro avg']['support'])}</td>
        </tr>
      </table>
    </div>""", unsafe_allow_html=True)

    # ── Veri bölünme özeti ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-radius:10px;padding:1rem 1.4rem;margin-top:8px;
                font-family:'Space Mono',monospace;font-size:0.82rem;">
      <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:0.6rem;">
        Veri Ön İşleme Özeti (Adım 2)
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;">
        <div><div style="color:{C['muted']}">Toplam Örnek</div>
             <div style="color:{C['text']};font-weight:700;">
               {len(X_train)+len(X_test)}</div></div>
        <div><div style="color:{C['muted']}">Eğitim (%80)</div>
             <div style="color:{C['green']};font-weight:700;">{len(X_train)}</div></div>
        <div><div style="color:{C['muted']}">Test (%20)</div>
             <div style="color:{C['yellow']};font-weight:700;">{len(X_test)}</div></div>
        <div><div style="color:{C['muted']}">Özellik Sayısı</div>
             <div style="color:{C['accent']};font-weight:700;">21</div></div>
      </div>
    </div>""", unsafe_allow_html=True)


# ── LSTM ─────────────────────────────────────────────────────────────────────
def _train_show_lstm(df, window_size):
    with st.spinner("🧠  LSTM modeli eğitiliyor (bu biraz sürebilir)..."):
        X_train, X_test, y_train, y_test, _ = prepare_lstm_data(df, window_size)
        model, history = train_lstm(X_train, y_train, X_test, y_test, epochs=30)

    if model is None:
        st.error("❌  TensorFlow kurulu değil.")
        st.code("pip install tensorflow", language="bash")
        return

    metrics = evaluate_model(model, X_test, y_test, "lstm")
    acc = metrics.get("accuracy", 0) * 100
    auc = metrics.get("auc", 0)

    st.success(f"✅  LSTM eğitimi tamamlandı!  Doğruluk: **{acc:.2f}%**")

    mc1,mc2,mc3 = st.columns(3)
    _card(mc1, "🎯 Doğruluk", f"{acc:.2f}%",
          color=C["green"] if acc>60 else C["yellow"])
    _card(mc2, "📐 AUC-ROC",  f"{auc:.4f}",
          color=C["green"] if auc>0.55 else C["yellow"])
    _card(mc3, "🪟 Pencere",  f"{window_size} gün",
          sub="LSTM sliding window")

    if history:
        fig = go.Figure()
        epochs = list(range(1, len(history.get("accuracy", [])) + 1))
        fig.add_trace(go.Scatter(x=epochs, y=history.get("accuracy", []),
            name="Train Accuracy", line=dict(color=C["accent"], width=2)))
        fig.add_trace(go.Scatter(x=epochs, y=history.get("val_accuracy", []),
            name="Val Accuracy", line=dict(color=C["purple"], width=2)))
        fig.add_trace(go.Scatter(x=epochs, y=history.get("loss", []),
            name="Train Loss", line=dict(color=C["red"], width=1.5, dash="dash")))
        fig.add_trace(go.Scatter(x=epochs, y=history.get("val_loss", []),
            name="Val Loss", line=dict(color=C["yellow"], width=1.5, dash="dash")))
        fig.update_layout(**_base_layout(
            "<b>LSTM Eğitim Eğrisi</b>", height=380,
            xaxis=dict(title="Epoch", gridcolor=C["border"]),
        ))
        st.plotly_chart(fig, use_container_width=True)

    # ── LSTM Mimari Gösterimi ──────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-radius:10px;padding:1.1rem 1.4rem;margin-top:8px;">
      <div style="color:{C['accent']};font-size:0.7rem;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:0.8rem;">
        LSTM Model Mimarisi (Adım 3)
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:0.82rem;line-height:2;">
        <div style="color:{C['green']}">→ Input: ({window_size}, 21)</div>
        <div style="color:{C['accent']}">→ Bidirectional LSTM (128) + BatchNorm + Dropout(0.3)</div>
        <div style="color:{C['accent']}">→ LSTM (64) + BatchNorm + Dropout(0.3)</div>
        <div style="color:{C['accent']}">→ LSTM (32) + BatchNorm + Dropout(0.2)</div>
        <div style="color:{C['purple']}">→ Dense (64, relu) + Dropout(0.2)</div>
        <div style="color:{C['purple']}">→ Dense (32, relu)</div>
        <div style="color:{C['yellow']}">→ Dense (1, sigmoid) — Binary Classification</div>
        <div style="color:{C['muted']};margin-top:6px;">
          Optimizer: Adam(lr=0.001) | Loss: binary_crossentropy
          | EarlyStopping(patience=8)
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
