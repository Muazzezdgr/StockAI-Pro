"""
utils/ui.py  -  Paylasilan HTML/CSS bilesenleri.

Bloomberg/TradingView tarzi yogun finans arayuzu icin tek bir kart ve
bilgi kutusu uygulamasi; Dashboard, Backtest, Karsilastirma, Portfoy ve
Alarmlar sayfalari ayni gorunumu almak icin bunu kullanir. Renkler
utils/chart_theme.COLORS uzerinden gelir (app.py :root paletiyle ayni),
bosluk ve font boyutlari app.py'de tanimlanan --space-* / --fs-* CSS
degiskenlerine referans verir (unsafe_allow_html ile ayni sayfaya
enjekte edildikleri icin :root degiskenleri her yerde gecerlidir).
"""
import streamlit as st

from utils.chart_theme import COLORS as C, BORDER_SOFT, BORDER_FAINT


def metric_card(col, label, value, sub="", color=None):
    """Kompakt metrik/bilgi karti (Bloomberg tarzi: kucuk ama net panel)."""
    color = color or C["accent"]
    with col:
        st.markdown(f"""
        <div style="background:{C['s2']};border:1px solid {BORDER_SOFT};
                    border-left:2px solid {color};border-radius:8px;
                    padding:var(--space-2) var(--space-3);
                    margin-bottom:var(--space-2);">
          <div style="color:{C['muted']};font-size:var(--fs-small);
                      font-family:'Space Mono',monospace;letter-spacing:0.5px;
                      text-transform:uppercase;">{label}</div>
          <div style="color:{C['text']};font-size:var(--fs-subheading);font-weight:700;
                      font-family:'Space Mono',monospace;margin:3px 0;">{value}</div>
          <div style="color:{color};font-size:var(--fs-small);">{sub}</div>
        </div>""", unsafe_allow_html=True)


def info_box(text_html, title=None, color=None):
    """Duz bilgilendirme kutusu. Renk sadece gercek bir uyari/durum tasiyorsa
    verilmeli; salt aciklayici notlar icin varsayilan (accent) kullanilir."""
    color = color or C["accent"]
    title_html = f'<b style="color:{color}">{title}</b> ' if title else ""
    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {BORDER_SOFT};
                border-left:2px solid {color};border-radius:8px;
                padding:var(--space-3) var(--space-4);
                margin-bottom:var(--space-3);font-size:var(--fs-body);
                color:{C['muted']};line-height:1.75;">
      {title_html}{text_html}
    </div>""", unsafe_allow_html=True)


def section_gap(size="sm"):
    """Tutarli dusey bosluk. size: 'xs' (4px), 'sm' (8px), 'md' (16px), 'lg' (24px)."""
    token = {"xs": "var(--space-1)", "sm": "var(--space-2)",
             "md": "var(--space-3)", "lg": "var(--space-4)"}[size]
    st.markdown(f"<div style='height:{token}'></div>", unsafe_allow_html=True)
