"""
pages/alarms.py  –  Fiyat Alarmları
"""
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

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


def get_current_price(symbol: str) -> dict:
    """Sembolün güncel fiyatını çek. Hata durumunda None döndür."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1d")
        if not data.empty:
            current_price = float(data["Close"].iloc[-1])
            return {"price": current_price, "success": True, "error": None}
        else:
            return {"price": None, "success": False, "error": "Veri bulunamadi"}
    except Exception as e:
        return {"price": None, "success": False, "error": str(e)}


def check_alarms():
    """Tüm alarmları kontrol et ve tetiklenenler işaretle."""
    if "alarms" not in st.session_state or not st.session_state["alarms"]:
        return []

    triggered = []
    for i, alarm in enumerate(st.session_state["alarms"]):
        if alarm["status"] == "tetiklendi":
            continue

        result = get_current_price(alarm["symbol"])
        if result["success"]:
            current_price = result["price"]
            alarm["current_price"] = current_price

            alarm_triggered = False
            if alarm["direction"] == "Uzerinde" and current_price >= alarm["target_price"]:
                alarm_triggered = True
            elif alarm["direction"] == "Altinda" and current_price <= alarm["target_price"]:
                alarm_triggered = True

            if alarm_triggered:
                alarm["status"] = "tetiklendi"
                alarm["triggered_at"] = datetime.now().strftime("%H:%M:%S")
                triggered.append(i)

    return triggered


def show_alarms():
    st.markdown('<p class="section-title">// FIYAT ALARLARI</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{C['s2']};border:1px solid {C['border']};
                border-left:3px solid {C['yellow']};border-radius:10px;
                padding:1rem 1.4rem;margin-bottom:1.2rem;font-size:0.85rem;
                color:{C['muted']};line-height:1.8;">
      <b style="color:{C['yellow']}">Bilgi:</b>
      Bu alarmlar yalnizca sayfa acikken kontrol edilir. Arka planda bildirim gonderilmez.
      Sayfayi kapat veya yenile oldugunda alarmlar sifirlanir.
    </div>""", unsafe_allow_html=True)

    if "alarms" not in st.session_state:
        st.session_state["alarms"] = []

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("Kontrol Et", key="check_alarms", use_container_width=True):
            with st.spinner("Alarmlar kontrol ediliyor..."):
                triggered_indices = check_alarms()
            if triggered_indices:
                st.session_state["_last_triggered"] = triggered_indices

    with col2:
        if st.button("Sayfayi Yenile", key="refresh_page", use_container_width=True):
            st.rerun()

    if "alarms" in st.session_state and any(a["status"] == "tetiklendi" for a in st.session_state["alarms"]):
        triggered_alarms = [a for a in st.session_state["alarms"] if a["status"] == "tetiklendi"]
        for alarm in triggered_alarms:
            st.warning(
                f"Alarm Tetiklendi: {alarm['symbol']} {alarm['direction'].lower()} "
                f"{alarm['target_price']} seviyesine ulasti! "
                f"Guncel: {alarm.get('current_price', '—'):.2f}"
            )

    st.subheader("Yeni Alarm Olustur")

    with st.form("add_alarm", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([2, 1.2, 1.5, 1])

        with c1:
            symbol = st.text_input("Sembol", placeholder="AAPL, BTC-USD, THYAO.IS")

        with c2:
            target_price = st.number_input("Hedef Fiyat", min_value=0.0, step=0.01, format="%.2f")

        with c3:
            direction = st.selectbox("Yon", ["Uzerinde", "Altinda"])

        with c4:
            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Alarm Ekle", use_container_width=True)

        if submitted:
            symbol = symbol.strip().upper()

            if not symbol:
                st.error("Sembol bos birakilamaz.")
            elif target_price <= 0:
                st.error("Hedef fiyat sifirdan buyuk olmalidir.")
            else:
                result = get_current_price(symbol)
                if not result["success"]:
                    st.error(f"Sembol bulunamadi: {result['error']}")
                else:
                    alarm_data = {
                        "symbol": symbol,
                        "target_price": float(target_price),
                        "direction": direction,
                        "current_price": result["price"],
                        "status": "bekliyor",
                        "created_at": datetime.now().strftime("%H:%M:%S"),
                        "triggered_at": None,
                    }
                    st.session_state["alarms"].append(alarm_data)
                    st.success(f"Alarm olusturuldu: {symbol} {direction.lower()} {target_price}")

    st.subheader("Aktif Alarmlar")

    if not st.session_state["alarms"]:
        st.info("Henuz aktif alarm yok.")
        return

    alarm_data_for_display = []
    for idx, alarm in enumerate(st.session_state["alarms"]):
        current = alarm.get("current_price", "—")
        if isinstance(current, float):
            current = f"{current:.2f}"

        alarm_data_for_display.append({
            "Sembol": alarm["symbol"],
            "Hedef": f"{alarm['target_price']:.2f}",
            "Yon": alarm["direction"],
            "Guncel": str(current),
            "Durum": alarm["status"],
            "Olustu": alarm["created_at"],
            "idx": idx,
        })

    df = pd.DataFrame(alarm_data_for_display)

    st.markdown(f"""
    <div style="overflow-x:auto;border:1px solid {C['border']};
                border-radius:8px;background:{C['s1']};padding:0;">
    """, unsafe_allow_html=True)

    cols = st.columns([1.5, 1, 1, 1, 1, 1.2, 1.5])
    with cols[0]:
        st.markdown(f"<b style='color:{C['accent']}'>Sembol</b>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<b style='color:{C['accent']}'>Hedef</b>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<b style='color:{C['accent']}'>Yon</b>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"<b style='color:{C['accent']}'>Guncel</b>", unsafe_allow_html=True)
    with cols[4]:
        st.markdown(f"<b style='color:{C['accent']}'>Durum</b>", unsafe_allow_html=True)
    with cols[5]:
        st.markdown(f"<b style='color:{C['accent']}'>Olustu</b>", unsafe_allow_html=True)
    with cols[6]:
        st.markdown(f"<b style='color:{C['accent']}'>", unsafe_allow_html=True)

    st.divider()

    for row in alarm_data_for_display:
        cols = st.columns([1.5, 1, 1, 1, 1, 1.2, 1.5])

        with cols[0]:
            st.text(row["Sembol"])
        with cols[1]:
            st.text(row["Hedef"])
        with cols[2]:
            st.text(row["Yon"])
        with cols[3]:
            st.text(row["Guncel"])
        with cols[4]:
            status_color = C["green"] if row["Durum"] == "tetiklendi" else C["yellow"]
            st.markdown(f"<span style='color:{status_color}'>{row['Durum']}</span>", unsafe_allow_html=True)
        with cols[5]:
            st.text(row["Olustu"])
        with cols[6]:
            if st.button("Sil", key=f"delete_{row['idx']}", use_container_width=True):
                st.session_state["alarms"].pop(row["idx"])
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Fiyat Alarlari — StockAI Pro",
        page_icon="⏰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    show_alarms()
