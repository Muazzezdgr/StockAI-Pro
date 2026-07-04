"""
utils/pdf_report.py
Dashboard analiz sonuclarindan PDF rapor olusturma (fpdf2).
"""
import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from utils.data_utils import format_market_cap

# Rapor renk paleti (RGB) - dashboard tema renkleriyle uyumlu
RGB = {
    "accent": (0, 123, 173),
    "purple": (92, 60, 168),
    "green":  (13, 130, 96),
    "red":    (180, 40, 40),
    "yellow": (170, 110, 10),
    "text":   (30, 35, 45),
    "muted":  (100, 110, 125),
    "border": (210, 214, 222),
    "s2":     (243, 245, 248),
}

SIGNAL_LABELS = {
    "AL": "AL (SATIN AL)",
    "SAT": "SAT",
    "TUT": "TUT (BEKLE)",
}


_ASCII_MAP = {
    "—": "-", "–": "-", "‘": "'", "’": "'",
    "“": '"', "”": '"', "…": "...",
    "İ": "I", "ı": "i", "Ş": "S", "ş": "s",
    "Ğ": "G", "ğ": "g",
}


def _safe(text):
    """PDF core font (latin-1) ile uyumlu olmayan karakterleri temizler."""
    if text is None:
        return "-"
    text = str(text)
    for src, dst in _ASCII_MAP.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "ignore").decode("latin-1")


def _rsi_yorumu(rsi_v):
    if rsi_v > 70:
        return "Asiri Alim"
    if rsi_v < 30:
        return "Asiri Satim"
    return "Normal"


def _macd_yorumu(macd_h):
    return "Yukselis egilimi" if macd_h > 0 else "Dusus egilimi"


def _generate_price_chart_image(df, symbol, max_bars=90):
    """Statik candlestick grafigi uretir, PNG bayt akisi olarak doner."""
    plot_df = df.tail(max_bars).copy()

    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    width = 0.6
    xs = range(len(plot_df))
    for i, (_, row) in zip(xs, plot_df.iterrows()):
        color = "#0d8260" if row["Close"] >= row["Open"] else "#b42828"
        ax.plot([i, i], [row["Low"], row["High"]], color=color, linewidth=0.8)
        lower = min(row["Open"], row["Close"])
        height = abs(row["Close"] - row["Open"]) or (row["High"] * 0.001 + 1e-6)
        ax.add_patch(plt.Rectangle((i - width / 2, lower), width, height, color=color))

    if "MA20" in plot_df.columns:
        ax.plot(list(xs), plot_df["MA20"].values, color="#007bad", linewidth=1.1, label="MA20")
    if "MA50" in plot_df.columns:
        ax.plot(list(xs), plot_df["MA50"].values, color="#aa6e0a", linewidth=1.1, label="MA50")

    n = len(plot_df)
    step = max(1, n // 8)
    ticks = list(range(0, n, step))
    ax.set_xticks(ticks)
    ax.set_xticklabels(
        [plot_df.index[t].strftime("%Y-%m-%d") for t in ticks],
        rotation=30, ha="right", fontsize=7,
    )
    ax.set_title(f"{symbol} Fiyat Grafigi (Candlestick)", fontsize=11)
    ax.set_ylabel("Fiyat")
    ax.legend(loc="upper left", fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


class _Report(FPDF):
    def header(self):
        self.set_fill_color(*RGB["accent"])
        self.rect(0, 0, self.w, 18, style="F")
        self.set_xy(10, 4)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "STOCKAI PRO")
        self.set_font("Helvetica", "", 9)
        self.set_xy(-70, 6)
        self.cell(60, 8, "Hisse Senedi Analiz Raporu", align="R")
        self.ln(16)
        self.set_text_color(*RGB["text"])

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*RGB["muted"])
        self.cell(0, 8, f"Sayfa {self.page_no()}/{{nb}}", align="C")


def _section_title(pdf, text):
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*RGB["accent"])
    pdf.cell(0, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*RGB["border"])
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)
    pdf.set_text_color(*RGB["text"])


def _kv_row(pdf, label, value, value_color=None):
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*RGB["muted"])
    pdf.cell(60, 7, label)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*(value_color or RGB["text"]))
    pdf.cell(0, 7, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def generate_pdf_report(symbol, info, df, last, change, rsi_v, macd_h,
                         pred_prob, signal, sent_agg, news, last_update):
    """
    Dashboard analiz verilerinden PDF rapor uretir ve bayt olarak doner.
    """
    pdf = _Report(format="A4", unit="mm")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Baslik: sembol, sirket adi, tarih ────────────────────────────────
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*RGB["text"])
    pdf.cell(0, 10, _safe(symbol), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*RGB["muted"])
    company_line = _safe(info.get("name", symbol))
    if info.get("sector") and info.get("sector") != "-":
        company_line += f"   |   Sektor: {_safe(info.get('sector'))}"
    pdf.cell(0, 6, company_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Rapor tarihi: {last_update.strftime('%Y-%m-%d %H:%M:%S')}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    # ── Fiyat Bilgileri ───────────────────────────────────────────────────
    _section_title(pdf, "1. Fiyat Bilgileri")
    chg_color = RGB["green"] if change >= 0 else RGB["red"]
    _kv_row(pdf, "Guncel Fiyat:", f"${last:,.2f}")
    _kv_row(pdf, "Gunluk Degisim:", f"{'+' if change >= 0 else ''}{change:.2f}%", value_color=chg_color)
    _kv_row(pdf, "Piyasa Degeri:", _safe(format_market_cap(info.get("market_cap"))))

    # ── Teknik Gostergeler ────────────────────────────────────────────────
    _section_title(pdf, "2. Teknik Gostergeler")
    rsi_color = RGB["red"] if rsi_v > 70 else (RGB["green"] if rsi_v < 30 else RGB["yellow"])
    macd_color = RGB["green"] if macd_h > 0 else RGB["red"]
    _kv_row(pdf, "RSI (14):", f"{rsi_v:.1f}  -  {_rsi_yorumu(rsi_v)}", value_color=rsi_color)
    _kv_row(pdf, "MACD Histogram:", f"{macd_h:+.4f}  -  {_macd_yorumu(macd_h)}", value_color=macd_color)

    # ── Model Tahmini ─────────────────────────────────────────────────────
    _section_title(pdf, "3. Model Tahmini")
    sig_color = RGB["green"] if signal == "AL" else (RGB["red"] if signal == "SAT" else RGB["yellow"])
    _kv_row(pdf, "Sinyal:", SIGNAL_LABELS.get(signal, signal), value_color=sig_color)
    _kv_row(pdf, "Model Guven Skoru:", f"{pred_prob*100:.1f}%")
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*RGB["muted"])
    aciklama = (
        "Guven skoru aciklamasi: Bu skor, Random Forest siniflandiricisinin en son veri "
        "noktasi icin hesapladigi yukari yonlu fiyat hareketi olasiligidir (0-100 arasi). "
        "Skorun %50 uzerinde olmasi modelin yukari yonlu hareket beklentisini, %50 altinda "
        "olmasi ise asagi yonlu hareket ihtimalinin daha yuksek goruldugunu gosterir. Bu "
        "deger bir kesinlik garantisi degildir; gecmis fiyat verilerine dayali istatistiksel "
        "bir tahmindir ve gercek piyasa belirsizliklerini tam olarak yansitmayabilir."
    )
    pdf.multi_cell(0, 5, aciklama, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*RGB["text"])

    # ── Haber Duygu Analizi ───────────────────────────────────────────────
    _section_title(pdf, "4. Haber Duygu Analizi Ozeti")
    overall_color = (RGB["green"] if sent_agg["overall"] == "Pozitif"
                      else (RGB["red"] if sent_agg["overall"] == "Negatif" else RGB["yellow"]))
    _kv_row(pdf, "Genel Durum:", _safe(sent_agg["overall"]), value_color=overall_color)
    _kv_row(pdf, "Ortalama Skor:", f"{sent_agg['avg_score']:+.2f}")
    _kv_row(pdf, "Pozitif / Negatif / Notr:",
            f"{sent_agg['positive']} / {sent_agg['negative']} / {sent_agg['neutral']}")
    if news:
        pdf.ln(1)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*RGB["muted"])
        pdf.cell(0, 6, "Son haber basliklari:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*RGB["text"])
        for n in news[:5]:
            label = _safe(n["sentiment"]["label"])
            title = _safe(n["title"])
            if len(title) > 95:
                title = title[:92] + "..."
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 5, f"- [{label}] {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Fiyat Grafigi ─────────────────────────────────────────────────────
    if pdf.get_y() + 107 > pdf.h - 25:
        pdf.add_page()
    _section_title(pdf, "5. Fiyat Grafigi")
    try:
        chart_buf = _generate_price_chart_image(df, symbol)
        avail_w = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.image(chart_buf, x=pdf.l_margin, w=avail_w)
    except Exception:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 6, "Grafik olusturulamadi.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Yasal Uyari ───────────────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_draw_color(*RGB["border"])
    pdf.set_fill_color(*RGB["s2"])
    y0 = pdf.get_y()
    disclaimer_text = (
        "YASAL UYARI: Bu rapor StockAI Pro platformu tarafindan egitim ve bilgilendirme "
        "amaciyla otomatik olarak uretilmistir. Raporda yer alan fiyat verileri, teknik "
        "gostergeler, model tahminleri ve haber duygu analizi sonuclari yatirim tavsiyesi, "
        "finansal danismanlik veya alim satim onerisi niteligi tasimaz. Istatistiksel "
        "modeller gecmis verilere dayanir ve gelecekteki fiyat hareketlerini garanti etmez. "
        "Yatirim kararlarinizi vermeden once lisansli bir yatirim danismanina basvurunuz."
    )
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*RGB["muted"])
    pdf.multi_cell(0, 4.6, disclaimer_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y1 = pdf.get_y()
    pdf.rect(pdf.l_margin - 2, y0 - 2, pdf.w - pdf.l_margin - pdf.r_margin + 4, y1 - y0 + 4)

    # ── Rapor kaynagi / uretim bilgisi ────────────────────────────────────
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*RGB["muted"])
    pdf.cell(0, 5, "Veri kaynagi: Yahoo Finance (yfinance) | Model: Random Forest siniflandirici",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, f"Rapor uretim tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | StockAI Pro v2.0",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    return bytes(pdf.output())
