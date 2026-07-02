"""
pages/portfolio.py  –  Portföy Takibi
"""
import streamlit as st
import pandas as pd

from utils.data_utils import fetch_stock_data

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


def _format_currency(value):
    if value is None:
        return "—"
    return f"₺{value:,.2f}"


def show_portfolio():
    st.markdown('<p class="section-title">// PORTFÖYÜM</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-left:3px solid {C['accent']};border-radius:10px;
                padding:1rem 1.4rem;margin-bottom:1.2rem;font-size:0.85rem;
                color:{C['muted']};line-height:1.8;">
      <b style="color:{C['accent']}">Portföy Takibi:</b>
      Sembol, adet ve alış fiyatını girerek varlıklarınızı takip edebilirsiniz.
      Portföy verisi bu oturum boyunca saklanır.
    </div>""", unsafe_allow_html=True)

    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = []

    with st.form("add_position", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([2.2, 1, 1.2, 1])
        with c1:
            symbol = st.text_input("Sembol", placeholder="AAPL, BTC-USD, THYAO.IS")
        with c2:
            quantity = st.number_input("Adet", min_value=0.0, step=1.0, format="%.6f")
        with c3:
            buy_price = st.number_input("Alış Fiyatı", min_value=0.0, step=1.0, format="%.6f")
        with c4:
            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("➕ Portföye Ekle", use_container_width=True)

        if submitted:
            symbol = symbol.strip()
            if not symbol:
                st.error("❌  Lütfen bir sembol girin.")
            elif quantity <= 0 or buy_price <= 0:
                st.error("❌  Adet ve alış fiyatı sıfırdan büyük olmalı.")
            else:
                st.session_state["portfolio"].append({
                    "symbol": symbol.upper(),
                    "quantity": float(quantity),
                    "buy_price": float(buy_price),
                })
                st.success(f"✅  {symbol.upper()} portföye eklendi.")

    portfolio = st.session_state["portfolio"]

    if not portfolio:
        st.info("ℹ️  Henüz portföyde varlık yok. Yukarıdan ekleyin.")
        return

    rows = []
    total_value = 0.0
    total_cost = 0.0
    total_pnl = 0.0

    for item in portfolio:
        symbol = item["symbol"]
        qty = float(item["quantity"])
        buy_price = float(item["buy_price"])

        try:
            df = fetch_stock_data(symbol, period="2y", interval="1d")
            current_price = None
            if not df.empty:
                current_price = float(df["Close"].iloc[-1])
        except Exception:
            current_price = None

        cost = qty * buy_price
        value = qty * current_price if current_price is not None else None
        pnl = value - cost if value is not None else None
        pnl_pct = (pnl / cost * 100) if pnl is not None and cost else None

        total_cost += cost
        if value is not None:
            total_value += value
            total_pnl += pnl

        rows.append({
            "symbol": symbol,
            "quantity": qty,
            "buy_price": buy_price,
            "current_price": current_price,
            "cost": cost,
            "value": value,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
        })

    c1, c2, c3 = st.columns(3)
    _card(c1, "💰 Toplam Portföy Değeri", _format_currency(total_value), color=C["accent"])
    _card(c2, "📈 Toplam Kar/Zarar", f"{total_pnl:+.2f} ₺", color=C["green"] if total_pnl >= 0 else C["red"])
    _card(c3, "📊 Toplam Maliyet", _format_currency(total_cost), color=C["yellow"])

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    display_df = pd.DataFrame([
        {
            "Sembol": row["symbol"],
            "Adet": f"{row['quantity']:,.2f}",
            "Alış Fiyatı": _format_currency(row["buy_price"]),
            "Güncel Fiyat": _format_currency(row["current_price"]),
            "Toplam Maliyet": _format_currency(row["cost"]),
            "Güncel Değer": _format_currency(row["value"]),
            "Kar/Zarar (₺)": f"{row['pnl']:+.2f} ₺" if row["pnl"] is not None else "—",
            "Kar/Zarar (%)": f"{row['pnl_pct']:+.2f}%" if row["pnl_pct"] is not None else "—",
        }
        for row in rows
    ])

    if not display_df.empty:
        styler = display_df.style.set_properties(**{
            "font-family": "Space Mono, monospace",
            "font-size": "0.82rem",
            "color": C["text"],
            "background-color": C["s2"],
        }).set_table_styles([
            {"selector": "th", "props": [("background-color", C["s1"]), ("color", C["muted"]), ("border-bottom", f"1px solid {C['border']}")]},
            {"selector": "td", "props": [("border-bottom", f"1px solid {C['border']}")]},
        ])

        def color_pnl(val):
            if val.startswith("+"):
                return f"color: {C['green']}"
            if val.startswith("-"):
                return f"color: {C['red']}"
            return f"color: {C['text']}"

        styler = styler.map(color_pnl, subset=["Kar/Zarar (₺)", "Kar/Zarar (%)"])
        st.dataframe(styler, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    delete_col, delete_btn = st.columns([3, 1])
    with delete_col:
        symbols = [item["symbol"] for item in portfolio]
        selected_to_delete = st.selectbox("Silinecek varlık", symbols, key="delete_symbol")
    with delete_btn:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Sil", use_container_width=True):
            st.session_state["portfolio"] = [item for item in portfolio if item["symbol"] != selected_to_delete]
            st.success(f"✅  {selected_to_delete} portföyden kaldırıldı.")
            st.rerun()
