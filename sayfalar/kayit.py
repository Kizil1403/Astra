"""
KAYIT — İlk açılış.
Kısa kayıt anketi. Dil sağ üstteki dil düğmesinden seçilir. Bilgiler veritabanındaki 'profil' tablosuna kaydedilir.
"""
import streamlit as st

import arayuz
import veritabani
from arayuz import html
from ceviri import t

# ---------------------------------------------------------------
# KAYIT ANKETİ
# ---------------------------------------------------------------
_, orta, _ = st.columns([1, 2.4, 1])
with orta:
    sol, sag = st.columns([4, 1], vertical_alignment="center")
    with sol:
        html(arayuz.marka_html())
    with sag:
        arayuz.dil_secici()
    arayuz.sayfa_basligi(t("kayit_ust"), t("kayit_baslik"), t("kayit_alt"))
    with st.container(border=True):
        ornek = {"ad": "Valentina", "soyad": "Tereşkova", "unvan": "Astronot", "cinsiyet": "Kadın",
                 "dogum_yili": 1987}
        bilgi = arayuz.profil_formu(ornek, t("kaydi_tamamla"), "kayit_formu")
        if bilgi:
            veritabani.profil_kaydet(bilgi)
            st.session_state["acilis_ekrani"] = True  # ana sayfadan önce logolu geçiş ekranı
            st.rerun()
    st.caption(t("veri_gizlilik"))
