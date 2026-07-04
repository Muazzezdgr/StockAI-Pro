"""
pages/disclaimer.py  –  Yasal Uyari
"""
import streamlit as st

C = {
    "bg": "#0a0e1a",
    "s1": "#111827",
    "s2": "#1a2235",
    "border": "#1e2d45",
    "accent": "#00d4ff",
    "purple": "#7c3aed",
    "green": "#10b981",
    "red": "#ef4444",
    "yellow": "#f59e0b",
    "text": "#e2e8f0",
    "muted": "#64748b",
}


def _section(number, title, body):
    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-left:3px solid {C['yellow']};border-radius:10px;
                padding:1rem 1.3rem;margin-bottom:0.9rem;">
      <div style="color:{C['yellow']};font-family:'Space Mono',monospace;
                  font-size:0.78rem;font-weight:700;letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:0.4rem;">
        {number}. {title}
      </div>
      <div style="color:{C['text']};font-size:0.92rem;line-height:1.7;">
        {body}
      </div>
    </div>""", unsafe_allow_html=True)


def show_disclaimer():
    st.markdown('<p class="section-title">// YASAL UYARI</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{C['s1']},{C['s2']});
                border:1px solid {C['red']};border-radius:14px;
                padding:1.3rem 1.6rem;margin-bottom:1.4rem;">
      <div style="color:{C['red']};font-family:'Space Mono',monospace;
                  font-weight:700;font-size:0.95rem;letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:0.5rem;">
        Onemli Uyari
      </div>
      <div style="color:{C['text']};font-size:0.95rem;line-height:1.7;">
        StockAI Pro platformunda yer alan hicbir icerik yatirim tavsiyesi,
        finansal danismanlik veya alim satim onerisi niteligi tasimaz.
        Lutfen platformu kullanmadan once asagidaki maddeleri dikkatlice okuyunuz.
      </div>
    </div>""", unsafe_allow_html=True)

    _section(
        "1", "Egitim ve Bilgilendirme Amaci",
        "Bu platform yalnizca egitim ve bilgilendirme amaciyla gelistirilmistir. "
        "Sitede sunulan veriler, grafikler, gostergeler ve model ciktilari "
        "yatirim tavsiyesi niteligi tasimaz ve bu sekilde yorumlanmamalidir."
    )
    _section(
        "2", "Istatistiksel Model Sinirlamalari",
        "Platformda uretilen tum tahmin ve analizler (LSTM, Random Forest ve "
        "benzeri makine ogrenmesi modelleri dahil), gecmis fiyat verilerine "
        "dayali istatistiksel modellerin ciktisidir. Bu modeller gelecekteki "
        "fiyat hareketlerini veya piyasa performansini garanti etmez."
    )
    _section(
        "3", "Kullanici Sorumlulugu",
        "Yatirim kararlari tamamen kullanicinin kendi sorumlulugundadir. "
        "Herhangi bir yatirim islemi gerceklestirmeden once lisansli bir "
        "yatirim danismanina veya yetkili bir finans kurulusuna danismaniz "
        "onemle tavsiye edilir."
    )
    _section(
        "4", "Veri Kaynagi ve Dogruluk",
        "Platformda kullanilan fiyat ve piyasa verileri Yahoo Finance (yfinance) "
        "araciligiyla ucuncu taraf bir kaynaktan temin edilmektedir. Bu "
        "verilerin dogrulugu, guncelligi veya eksiksizligi garanti edilmemektedir."
    )
    _section(
        "5", "Gecmis Performans Uyarisi",
        "Backtest sonuclari dahil olmak uzere, gecmiste elde edilen performans "
        "verileri gelecekteki sonuclarin bir garantisi degildir. Gecmiste elde "
        "edilen basari, gelecekte ayni sonucun alinacagi anlamina gelmez."
    )

    st.markdown(f"""
    <div style="margin-top:1.8rem;padding-top:1rem;border-top:1px solid {C['border']};
                color:{C['muted']};font-size:0.75rem;font-family:'Space Mono',monospace;">
      Surum: v2.0 | Guncelleme Tarihi: 04.07.2026
    </div>""", unsafe_allow_html=True)
