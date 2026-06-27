"""pages/about.py – Hakkında ve Proje Bilgisi"""
import streamlit as st

C = {"s2":"#1a2235","border":"#1e2d45","accent":"#00d4ff","purple":"#7c3aed",
     "green":"#10b981","text":"#e2e8f0","muted":"#64748b"}

def show_about():
    st.markdown('<p class="section-title">// PROJE HAKKINDA</p>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{C['s2']},#0d1526);
                border:1px solid {C['border']};border-radius:16px;
                padding:2rem;margin-bottom:1.5rem;">
      <h2 style="font-family:'Space Mono',monospace;margin:0 0 0.5rem;
                 background:linear-gradient(135deg,{C['accent']},{C['purple']});
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        StockAI Pro
      </h2>
      <div style="color:{C['muted']};font-family:'Space Mono',monospace;
                  font-size:0.8rem;margin-bottom:1rem;">
        v2.0 — LSTM + Random Forest + NLP
      </div>
      <p style="color:#94a3b8;line-height:1.8;margin:0;">
        Geçmiş hisse senedi verileri kullanılarak ertesi gün fiyat yönü tahmini yapan
        kapsamlı bir yapay zeka sistemi. Bidirectional LSTM derin öğrenme modeli,
        Random Forest algoritması ve haber duygu analizi birlikte kullanılarak
        ensemble tahmin üretilmektedir.
      </p>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;">
      <div style="background:{C['s2']};border:1px solid {C['border']};
                  border-radius:12px;padding:1.4rem;">
        <div style="color:{C['accent']};font-family:'Space Mono',monospace;
                    font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;
                    margin-bottom:0.8rem;">Grup Bilgileri</div>
        <table style="font-family:'Space Mono',monospace;font-size:0.82rem;width:100%;">
          <tr><td style="color:{C['muted']};padding:4px 0">Öğrenci 1</td>
              <td style="color:{C['text']};padding:4px 8px">Muazzez Doğru</td>
              <td style="color:{C['muted']};font-size:0.75rem">90240000271</td></tr>
          <tr><td style="color:{C['muted']};padding:4px 0">Öğrenci 2</td>
              <td style="color:{C['text']};padding:4px 8px">Yunus Emre Kaymakcı</td>
              <td style="color:{C['muted']};font-size:0.75rem">90240000221</td></tr>
          <tr><td style="color:{C['muted']};padding:4px 0">Öğrenci 3</td>
              <td style="color:{C['text']};padding:4px 8px">Elif Yıldırım</td>
              <td style="color:{C['muted']};font-size:0.75rem">90240000220</td></tr>
          <tr><td style="color:{C['muted']};padding:4px 0">Proje</td>
              <td style="color:{C['accent']};padding:4px 8px" colspan="2">C-5 — Hisse Senedi Yön Tahmini</td></tr>
        </table>
      </div>
      <div style="background:{C['s2']};border:1px solid {C['border']};
                  border-radius:12px;padding:1.4rem;">
        <div style="color:{C['accent']};font-family:'Space Mono',monospace;
                    font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;
                    margin-bottom:0.8rem;">Teknik Stack</div>
        <div style="font-family:'Space Mono',monospace;font-size:0.82rem;
                    line-height:2.2;">
          <div><span style="color:{C['muted']}">Dil       </span>
               <span style="color:{C['text']}">Python 3.10+</span></div>
          <div><span style="color:{C['muted']}">Derin Öğr </span>
               <span style="color:{C['text']}">TensorFlow / Keras (BiLSTM)</span></div>
          <div><span style="color:{C['muted']}">ML        </span>
               <span style="color:{C['text']}">Scikit-learn (RF, GB)</span></div>
          <div><span style="color:{C['muted']}">Arayüz    </span>
               <span style="color:{C['text']}">Streamlit + Plotly</span></div>
          <div><span style="color:{C['muted']}">Veri      </span>
               <span style="color:{C['text']}">yfinance (BIST + ABD)</span></div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Değerlendirme kriterleri
    criteria = [
        ("%20","Veri Ön İşleme & EDA",
         "21 teknik gösterge, MinMaxScaler, sliding window, eksik değer analizi"),
        ("%30","Model Geliştirme & Eğitim",
         "BiLSTM + Random Forest + Gradient Boosting, %80/%20 split, hiperparametre"),
        ("%20","Çalışır Arayüz / Demo",
         "Streamlit dashboard, 5 sayfa, canlı tahmin, backtest simülasyonu"),
        ("%15","Teknik Rapor & Kod Kalitesi",
         "Hücre başlıkları, yorum satırları, modüler yapı"),
        ("%15","Sunum & Soru-Cevap",
         "8–10 dk. canlı demo, her grup üyesi sunum yapıyor"),
    ]
    st.markdown(f"""
    <div style="color:{C['accent']};font-family:'Space Mono',monospace;
                font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;
                margin-bottom:0.8rem;">Değerlendirme Kriterleri</div>""",
                unsafe_allow_html=True)

    for weight, title, desc in criteria:
        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {C['border']};
                    border-radius:10px;padding:0.9rem 1.2rem;
                    margin-bottom:0.5rem;display:flex;gap:1.2rem;
                    align-items:flex-start;">
          <div style="color:{C['accent']};font-family:'Space Mono',monospace;
                      font-weight:800;font-size:1.1rem;min-width:45px;">{weight}</div>
          <div>
            <div style="color:{C['text']};font-weight:600;margin-bottom:3px;">
              {title}</div>
            <div style="color:{C['muted']};font-size:0.8rem;">{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)
