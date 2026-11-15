"""
GRAFİKLER — Geçmiş ve yeni değerler. Seçilen günün grafiği, son 14 günün ortalamaları, veri tablosu.
Sayfa her gün yeni verilerle kendiliğinden güncellenir.
"""
import io
from datetime import date

import pandas as pd

import streamlit as st

import arayuz
import ayarlar
import grafikler
import saat_simulatoru
import saglik_motoru
import veritabani
from arayuz import html
from ceviri import t, tx

arayuz.sayfa_basligi(t("grafik_ust"), t("grafik_baslik"), t("grafik_alt"))

gunler = veritabani.olcum_gunleri()
if len(gunler) <= 1:
    st.info(t("demo_veri_oneri"), icon=":material/info:")
    if st.button(t("demo_veri_olustur"), icon=":material/history:"):
        with st.spinner(t("demo_veri_uretiliyor")):
            saat_simulatoru.gecmis_veri_uret(14, veritabani.ayar("ortam"))
        st.rerun()

c1, c2 = st.columns([1.3, 1])
kod = c1.segmented_control(t("deger_sec"), options=list(ayarlar.METRIKLER),
                           format_func=lambda k: tx(ayarlar.METRIKLER[k]["ad"]), default="nabiz",
                           key="grafik_metrik") or "nabiz"
bugun = date.today().isoformat()
secili_gun = c2.selectbox(t("gun_sec"), gunler or [bugun],
                          format_func=lambda g: t("bugun") if g == bugun else
                          date.fromisoformat(g).strftime("%d.%m.%Y"))
m = ayarlar.METRIKLER[kod]
birim = tx(m["birim"])
canli = veritabani.ayar("canli") == "1" and secili_gun == bugun


@st.fragment(run_every=int(veritabani.ayar("olcum_araligi")) if canli else None)
def gun_paneli():
    df = veritabani.gunun_olcumleri(secili_gun)
    if df.empty:
        st.warning(t("veri_yok"))
        return
    seri = df[kod]
    normal_oran = sum(saglik_motoru.durum_bul(kod, v) == "yesil" for v in seri) / len(seri) * 100
    kartlar = [
        (t("ortalama"), saglik_motoru.sayi(kod, seri.mean())),
        (t("en_dusuk"), saglik_motoru.sayi(kod, seri.min())),
        (t("en_yuksek"), saglik_motoru.sayi(kod, seri.max())),
        (t("normal_aralikta"), f"{normal_oran:.0f}%"),
    ]
    for sutun, (ad, deger) in zip(st.columns(4), kartlar):
        sutun.markdown(f'<div class="kutu" style="padding:14px"><div class="kutu-ust">{ad}</div>'
                       f'<div class="kutu-deger" style="font-size:1.4rem">{deger}</div></div>',
                       unsafe_allow_html=True)
    st.write("")
    with st.container(border=True):
        arayuz.bolum_basligi(tx(m["ad"]).upper(), t("gun_grafigi_baslik", birim=birim))
        html(f'<div class="gri">{t("normal")}: {saglik_motoru.normal_aralik_yazisi(kod)} {birim} · '
             f'{t("olcum_sayisi")}: {len(df)}</div>')
        st.plotly_chart(grafikler.trend_grafigi(df, kod, None, birim, yukseklik=320),
                        config={"displayModeBar": False}, key="gun_grafigi")


gun_paneli()

with st.container(border=True):
    arayuz.bolum_basligi(t("saatlik_ust"), t("saatlik_baslik"))
    saatlik = veritabani.saatlik_ortalamalar(secili_gun)
    if len(saatlik) >= 1:
        st.plotly_chart(grafikler.saatlik_ortalama_grafigi(saatlik, kod, birim, saglik_motoru.durum_bul,
                                                           t("uyari_cizgi"), t("kritik_cizgi")),
                        config={"displayModeBar": False}, key="saatlik_grafik")
        st.caption(t("renk_aciklama_saatlik"))
    else:
        st.caption(t("veri_yok"))


def otuz_dakikalik(df):
    """Ölçümleri 30 dakikalık dilimlere toplar: her satır o yarım saatin ortalaması."""
    sayisal = [k for k in ayarlar.METRIKLER if k in df.columns]
    gruplu = df.set_index("zaman").resample("30min")
    tablo = gruplu[sayisal].mean().round(1)
    tablo["ortam"] = gruplu["ortam"].first()
    tablo = tablo.dropna(subset=sayisal, how="all").reset_index()
    tablo.insert(0, "id", range(len(tablo)))
    return tablo[["id", "zaman", "ortam"] + sayisal]


def indirilecek_tablo(df):
    """İndirilecek tablo: okunur sütun adları, tarih ve saat ayrı, sayılar düzgün."""
    tablo = df.drop(columns=["id"]).copy()
    tablo.insert(0, t("tarih"), tablo["zaman"].dt.strftime("%d.%m.%Y"))
    tablo.insert(1, t("saat"), tablo["zaman"].dt.strftime("%H:%M:%S"))
    tablo = tablo.drop(columns=["zaman"])
    tablo["ortam"] = tablo["ortam"].map(lambda o: tx(ayarlar.ORTAMLAR[o]["ad"]) if o in ayarlar.ORTAMLAR else o)
    return tablo.rename(columns={"ortam": t("ortam"),
                                 **{k: f"{tx(v['ad'])} ({tx(v['birim'])})" for k, v in ayarlar.METRIKLER.items()}})


with st.expander(t("veri_tablosu"), icon=":material/table:"):
    df = veritabani.gunun_olcumleri(secili_gun)
    if not df.empty:
        tablo = indirilecek_tablo(otuz_dakikalik(df))
        st.caption(t("tablo_aciklama"))
        st.dataframe(tablo.iloc[::-1], hide_index=True)
        i1, i2 = st.columns(2)
        # Excel dosyası: her değer kendi sütununda, doğrudan açılır
        excel = io.BytesIO()
        with pd.ExcelWriter(excel, engine="openpyxl") as yazici:
            tablo.to_excel(yazici, index=False, sheet_name=secili_gun)
            sayfa = yazici.sheets[secili_gun]
            for sutun in sayfa.columns:
                sayfa.column_dimensions[sutun[0].column_letter].width = max(12, len(str(sutun[0].value)) + 2)
        i1.download_button(t("excel_indir"), excel.getvalue(), file_name=f"astra_olcumler_{secili_gun}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           icon=":material/table_view:", type="primary")
        # CSV: Türkçe Excel'in doğru ayırması için noktalı virgül, Türkçe karakterler için BOM
        i2.download_button(t("csv_indir"), tablo.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                           file_name=f"astra_olcumler_{secili_gun}.csv", mime="text/csv",
                           icon=":material/download:")
