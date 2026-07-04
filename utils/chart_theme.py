"""
utils/chart_theme.py  -  Tum Plotly grafikleri icin ortak profesyonel tema.

Bu modul app.py / .streamlit/config.toml icindeki CSS renk paletini
(--accent, --green, --red, vb.) baz alir; yeni renk eklemez, sadece
mevcut paleti (ince cizgiler, soluk izgaralar, gradyanli alanlar,
tutarli tipografi) daha etkili bicimde uygular.
"""

# ── Palet (app.py :root degiskenleriyle birebir ayni) ────────────────────────
COLORS = {
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

FONT_FAMILY = "Space Mono, monospace"

# ── Tutarli tipografi olcekleri ──────────────────────────────────────────────
TITLE_SIZE  = 13.5
AXIS_TITLE  = 11
TICK_SIZE   = 10.5
LEGEND_SIZE = 10.5
HOVER_SIZE  = 11.5

# ── Tutarli, ince/zarif cizgi kalinliklari ───────────────────────────────────
LINE_HAIR   = 1.0   # yardimci / ikincil cizgiler (MA10, referans cizgileri)
LINE_THIN   = 1.3   # ikincil seri (MA50, sinyal cizgisi)
LINE_REG    = 1.5   # standart seri (RSI, MACD, karsilastirma)
LINE_MAIN   = 1.75  # birincil / vurgulanan seri (MA20, model getirisi, ROC)

PLOT_BG = "rgba(17,24,39,0.55)"


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgba(hex_color, alpha):
    """Mevcut palet renklerini opaklik ile kullanmak icin yardimci fonksiyon."""
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{alpha})"


# Izgaralar cok belirgin olmasin: muted renk, dusuk opaklik
GRID_COLOR = rgba(COLORS["muted"], 0.14)
AXIS_LINE_COLOR = rgba(COLORS["muted"], 0.28)


def area_fillgradient(hex_color, top_alpha=0.24, bottom_alpha=0.0):
    """Alan grafiklerine (RSI, ROC, portfoy vb.) dikey derinlik gradyani."""
    return dict(
        type="vertical",
        colorscale=[[0, rgba(hex_color, top_alpha)], [1, rgba(hex_color, bottom_alpha)]],
    )


def base_axis(title=None, **extra):
    ax = dict(
        gridcolor=GRID_COLOR, showgrid=True, gridwidth=1,
        zeroline=False,
        showline=True, linecolor=AXIS_LINE_COLOR, linewidth=1,
        tickfont=dict(size=TICK_SIZE, color=COLORS["muted"], family=FONT_FAMILY),
    )
    if title:
        ax["title"] = dict(text=title, font=dict(size=AXIS_TITLE, color=COLORS["muted"]))
    ax.update(extra)
    return ax


def bottom_legend(**extra):
    """Grafik icerigini kapatmayan, alt ortali, sade legend."""
    base = dict(
        orientation="h",
        yanchor="bottom", y=-0.24,
        xanchor="center", x=0.5,
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
        font=dict(size=LEGEND_SIZE, color=COLORS["muted"], family=FONT_FAMILY),
    )
    base.update(extra)
    return base


def hover_style(**extra):
    base = dict(
        bgcolor=rgba(COLORS["s2"], 0.95),
        bordercolor=COLORS["border"],
        font=dict(color=COLORS["text"], family=FONT_FAMILY, size=HOVER_SIZE),
    )
    base.update(extra)
    return base


def base_layout(title="", height=350, x_title=None, y_title=None,
                 show_legend=True, margin=None, **extra):
    """
    Guvenli, tutarli plot layout uretici.
    extra icinde xaxis/yaxis/legend gibi dict alanlar varsa base ile
    birlestirilir (tamamen degistirmez), boylece cakisma olmaz.
    """
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(color=COLORS["text"], family=FONT_FAMILY, size=TICK_SIZE),
        margin=margin or dict(l=52, r=24, t=52, b=56 if show_legend else 30),
        title=dict(text=title, font=dict(size=TITLE_SIZE, color=COLORS["text"]),
                   x=0.01, xanchor="left"),
        xaxis=base_axis(x_title),
        yaxis=base_axis(y_title),
        height=height,
        hoverlabel=hover_style(),
    )
    if show_legend:
        base["legend"] = bottom_legend()
    else:
        base["showlegend"] = False

    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = {**base[k], **v}
        else:
            base[k] = v
    return base


def modebar_config(filename="stockai_chart", extra_remove=None):
    remove = ["lasso2d"]
    if extra_remove:
        remove += extra_remove
    return {
        "scrollZoom": True,
        "displayModeBar": True,
        "modeBarButtonsToRemove": remove,
        "toImageButtonOptions": {"format": "png", "filename": filename, "scale": 2},
    }
