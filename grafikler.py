"""
GRAFİKLER — Monitör tarzı grafikler (Plotly).
"""
import numpy as np
import plotly.graph_objects as go

import ayarlar

ARKA = "#0c1524"
IZGARA = "#18263a"
CIZGI = "#38bdf8"


def _stil(fig, yukseklik, baslik=None):
    fig.update_layout(
        height=yukseklik, margin=dict(l=8, r=8, t=36 if baslik else 8, b=8),
        paper_bgcolor=ARKA, plot_bgcolor=ARKA, font=dict(color="#8aa0b8", size=12),
        showlegend=False, hoverlabel=dict(bgcolor="#0f1d33"),
    )
    if baslik:
        fig.update_layout(title=dict(text=baslik, font=dict(size=13, color="#cbd5e1"), x=0.01))
    fig.update_xaxes(gridcolor=IZGARA, zeroline=False, linecolor=IZGARA)
    fig.update_yaxes(gridcolor=IZGARA, zeroline=False, linecolor=IZGARA)
    return fig


def ekg_dalgasi(nabiz: float, renk: str, baslik: str):
    """Nabız değerine göre EKG benzeri çizgi (gösterim amaçlı)."""
    t = np.linspace(0, 5.0, 1000)
    periyot = 60.0 / max(nabiz, 30)
    faz = (t % periyot) / periyot

    def tepe(merkez, yukseklik, genislik):
        return yukseklik * np.exp(-((faz - merkez) ** 2) / (2 * genislik ** 2))

    y = (tepe(0.18, 0.12, 0.025) + tepe(0.36, -0.12, 0.008) + tepe(0.39, 1.0, 0.010)
         + tepe(0.42, -0.25, 0.010) + tepe(0.65, 0.30, 0.045)) + np.random.normal(0, 0.015, len(t))
    fig = go.Figure(go.Scatter(x=t, y=y, mode="lines", line=dict(color=renk, width=2), hoverinfo="skip"))
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False, range=[-0.4, 1.15])
    return _stil(fig, 160, baslik)


def _y_araligi(degerler, alt, ust):
    y_min = min(degerler.min(), alt) * 0.92
    y_max = max(degerler.max(), min(ust, alt * 1.5)) * 1.08
    return [y_min, y_max]


def trend_grafigi(df, kod: str, baslik: str, birim: str, yukseklik: int = 260, x_aralik=None):
    """Bir değerin zaman içindeki değişimi. Yeşil bant = normal aralık.
    x_aralik verilirse yatay eksen o saatler arasını gösterir (saat:dakika olarak)."""
    alt, ust = ayarlar.METRIKLER[kod]["yesil"]
    fig = go.Figure()
    fig.add_hrect(y0=alt, y1=ust, fillcolor=ayarlar.RENKLER["yesil"], opacity=0.08, line_width=0)
    fig.add_trace(go.Scatter(
        x=df["zaman"], y=df[kod], mode="lines+markers",
        line=dict(color=CIZGI, width=2), marker=dict(size=5, color=ARKA, line=dict(color=CIZGI, width=2)),
        hovertemplate="%{x|%d.%m %H:%M}<br>%{y} " + birim + "<extra></extra>",
    ))
    fig.update_yaxes(range=_y_araligi(df[kod], alt, ust))
    fig = _stil(fig, yukseklik, baslik)
    if x_aralik:
        fig.update_xaxes(range=list(x_aralik), tickformat="%H:%M")
    return fig


def gunluk_ortalama_grafigi(df, kod: str, baslik: str, birim: str, durum_bul):
    """Günlük ortalamalar: her çubuk durumuna göre renkli."""
    alt, ust = ayarlar.METRIKLER[kod]["yesil"]
    renkler = [ayarlar.RENKLER[durum_bul(kod, v)] for v in df[kod]]
    fig = go.Figure(go.Bar(
        x=df["gun"], y=df[kod], marker_color=renkler, marker_line_width=0,
        hovertemplate="%{x}<br>%{y:.1f} " + birim + "<extra></extra>",
    ))
    fig.add_hrect(y0=alt, y1=ust, fillcolor=ayarlar.RENKLER["yesil"], opacity=0.06, line_width=0)
    fig.update_yaxes(range=_y_araligi(df[kod], alt, ust))
    fig.update_layout(bargap=0.35)
    return _stil(fig, 260, baslik)


def ruh_hali_grafigi(df, etiketler: dict, baslik: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["zaman"], y=df["ruh_hali"], name=etiketler["ruh_hali"],
                             mode="lines+markers", line=dict(color="#22c55e")))
    fig.add_trace(go.Scatter(x=df["zaman"], y=df["enerji"], name=etiketler["enerji"],
                             mode="lines+markers", line=dict(color=CIZGI)))
    fig.add_trace(go.Scatter(x=df["zaman"], y=df["stres"] / 2, name=etiketler["stres"],
                             mode="lines+markers", line=dict(color="#ef4444")))
    fig = _stil(fig, 280, baslik)
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.18))
    fig.update_yaxes(range=[0, 5.5])
    return fig


ESIK_CIZGI = "#5eead4"


def esik_cizgileri(kod: str, etiket_uyari: str, etiket_kritik: str) -> list:
    """Bir değerin Uyarı / Kritik sınır çizgileri: [(değer, etiket, renk, çizgi tipi), ...]"""
    m = ayarlar.METRIKLER[kod]
    (y_alt, y_ust), (s_alt, s_ust) = m["yesil"], m["sari"]
    cizgiler = []
    if y_ust < s_ust:  # üst sınırı anlamlı olan değerler (nabız, ısı, solunum)
        cizgiler += [(y_ust, etiket_uyari, ayarlar.RENKLER["sari"], "dash"),
                     (s_ust, etiket_kritik, ayarlar.RENKLER["kirmizi"], "dot")]
    if y_alt > s_alt:  # alt sınırı anlamlı olan değerler
        cizgiler += [(y_alt, etiket_uyari, ayarlar.RENKLER["sari"], "dash"),
                     (s_alt, etiket_kritik, ayarlar.RENKLER["kirmizi"], "dot")]
    return cizgiler


def esik_grafigi(x, y, cizgiler: list, birim: str, yukseklik: int = 250, x_bicim: str = "%H:%M"):
    """Gönderilen örnekteki gibi: tek renk çizgi, son noktada işaret, kesikli Uyarı ve noktalı Kritik çizgileri."""
    y = list(y)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(x), y=y, mode="lines", line=dict(color=ESIK_CIZGI, width=2),
                             hovertemplate="%{x|" + x_bicim + "}<br>%{y} " + birim + "<extra></extra>"))
    fig.add_trace(go.Scatter(x=[list(x)[-1]], y=[y[-1]], mode="markers", hoverinfo="skip",
                             marker=dict(color=ESIK_CIZGI, size=9, line=dict(color=ARKA, width=2))))
    for deger, etiket, renk, tip in cizgiler:
        fig.add_hline(y=deger, line_dash=tip, line_color=renk, line_width=1.3, opacity=0.9,
                      annotation_text=etiket, annotation_position="right",
                      annotation_font=dict(color=renk, size=11))
    tum = y + [c[0] for c in cizgiler]
    pay = (max(tum) - min(tum)) * 0.12 or 1
    fig.update_yaxes(range=[min(tum) - pay, max(tum) + pay], showgrid=True)
    fig.update_xaxes(showgrid=False, tickformat=x_bicim)
    fig = _stil(fig, yukseklik)
    fig.update_layout(margin=dict(l=8, r=60, t=10, b=8))
    return fig


def puan_grafigi(df):
    """Son günlerde kazanılan günlük puanlar."""
    fig = go.Figure(go.Bar(x=df["tarih"], y=df["puan"], marker_color="#60a5fa", marker_line_width=0,
                           hovertemplate="%{x}<br>%{y}<extra></extra>"))
    fig.update_layout(bargap=0.35)
    return _stil(fig, 220)


def saatlik_ortalama_grafigi(df, kod: str, birim: str, durum_bul, etiket_uyari: str, etiket_kritik: str):
    """Seçilen günün saatlik ortalamaları: her çubuk durumuna göre renkli, Uyarı/Kritik çizgileriyle."""
    renkler = [ayarlar.RENKLER[durum_bul(kod, v)] for v in df[kod]]
    fig = go.Figure(go.Bar(
        x=df["saat"], y=df[kod], marker_color=renkler, marker_line_width=0,
        hovertemplate="%{x}<br>%{y:.1f} " + birim + "<extra></extra>",
    ))
    cizgiler = esik_cizgileri(kod, etiket_uyari, etiket_kritik)
    for deger, etiket, renk, tip in cizgiler:
        fig.add_hline(y=deger, line_dash=tip, line_color=renk, line_width=1.2, opacity=0.85,
                      annotation_text=etiket, annotation_position="right", annotation_font=dict(color=renk, size=11))
    tum = list(df[kod]) + [c[0] for c in cizgiler]
    pay = (max(tum) - min(tum)) * 0.12 or 1
    fig.update_yaxes(range=[max(0, min(tum) - pay), max(tum) + pay])
    fig.update_xaxes(type="category", tickangle=0)
    fig.update_layout(bargap=0.3)
    fig = _stil(fig, 280)
    fig.update_layout(margin=dict(l=8, r=60, t=10, b=8))
    return fig
