"""
GÜNLÜK — Yazı, ses ve video kayıtları. Tarihe veya ada göre sıralama, arama, eski kayıtlara erişim.
"""
import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

import arayuz
import ayarlar
import veritabani
from ceviri import t, tx

arayuz.sayfa_basligi(t("gunluk_ust"), t("gunluk_baslik"), t("gunluk_alt"))

TURLER = {"yazi": t("tur_yazi"), "ses": t("tur_ses"), "video": t("tur_video")}
TUR_IKON = {"yazi": ":material/edit_note:", "ses": ":material/mic:", "video": ":material/videocam:"}

if "form_no" not in st.session_state:  # kayıttan sonra formu temizlemek için
    st.session_state.form_no = 0
n = st.session_state.form_no

# ---------------------------------------------------------------
# YENİ KAYIT
# ---------------------------------------------------------------
with st.container(border=True):
    arayuz.bolum_basligi(t("yeni_kayit_ust"), t("yeni_kayit_baslik"))
    c1, c2 = st.columns([2, 1])
    baslik = c1.text_input(t("kayit_basligi"), key=f"baslik_{n}", placeholder=t("kayit_basligi_ornek"))
    tur = c2.segmented_control(t("kayit_turu"), options=list(TURLER), format_func=TURLER.get,
                               default=st.session_state.pop("gunluk_tur", "yazi"), key=f"tur_{n}") or "yazi"
    ruh = st.select_slider(t("bugunku_ruh_halin"), options=[1, 2, 3, 4, 5], value=3,
                           format_func=lambda x: tx(ayarlar.RUH_HALI_SECENEKLERI[x]), key=f"ruh_{n}")
    metin = st.text_area(t("kayit_metni") if tur == "yazi" else t("kayit_notu"), key=f"metin_{n}", height=140)

    dosya, uzanti = None, None
    if tur == "ses":
        st.caption(t("ses_aciklama"))
        if hasattr(st, "audio_input"):
            ses = st.audio_input(t("ses_kaydet"), key=f"ses_{n}")
        else:  # çok eski Streamlit sürümü
            ses = None
            st.warning(t("ses_surum_uyari"))
        if ses is not None:
            dosya, uzanti = ses.getvalue(), "wav"
            st.success(t("ses_hazir", sn=f"{len(dosya) / 32000:.0f}"), icon=":material/mic:")
        with st.expander(t("ses_dosya_yukle_baslik"), icon=":material/upload_file:"):
            ses_dosyasi = st.file_uploader(t("ses_dosya_yukle"), type=["wav", "mp3", "m4a", "ogg", "webm"],
                                           key=f"ses_dosya_{n}")
            if ses_dosyasi is not None:
                dosya, uzanti = ses_dosyasi.getvalue(), ses_dosyasi.name.rsplit(".", 1)[-1].lower()
    elif tur == "video":
        st.caption(t("video_aciklama"))
        video = st.file_uploader(t("video_yukle"), type=["mp4", "mov", "webm", "m4v"], key=f"video_{n}")
        if video is not None:
            dosya, uzanti = video.getvalue(), video.name.rsplit(".", 1)[-1].lower()

    if st.button(t("kaydi_kaydet"), type="primary", icon=":material/save:"):
        if not baslik.strip() and tur != "yazi":  # ses/video için başlık yazılmadıysa otomatik başlık
            baslik = f"{TURLER[tur]} · {datetime.now():%d.%m.%Y %H:%M}"
        if not baslik.strip():
            st.error(t("baslik_gerekli"))
        elif tur != "yazi" and dosya is None:
            st.error(t("dosya_gerekli"))
        elif tur == "yazi" and not metin.strip():
            st.error(t("metin_gerekli"))
        else:
            yol = veritabani.dosya_kaydet(dosya, uzanti) if dosya is not None else None
            veritabani.gunluk_ekle(baslik.strip(), tur, metin.strip(), ruh, yol)
            if veritabani.gorev_tamamla("gunluk", 20):
                st.session_state["bildirim"] = t("gunluk_kaydedildi_puan")
            else:
                st.session_state["bildirim"] = t("gunluk_kaydedildi")
            st.session_state.form_no += 1
            st.rerun()

st.write("")

# ---------------------------------------------------------------
# ESKİ KAYITLAR
# ---------------------------------------------------------------
arayuz.bolum_basligi(t("arsiv_ust"), t("arsiv_baslik"))
kayitlar = veritabani.gunluk_kayitlari()

f1, f2, f3, f4 = st.columns([2, 1.2, 1.2, 1.2])
arama = f1.text_input(t("ara"), placeholder=t("ara_ornek"), label_visibility="collapsed")
siralamalar = {"yeni": t("sira_yeni"), "eski": t("sira_eski"), "az": t("sira_az"), "za": t("sira_za")}
sira = f2.selectbox(t("sirala"), list(siralamalar), format_func=siralamalar.get, label_visibility="collapsed")
tur_filtre = f3.selectbox(t("tur"), ["hepsi"] + list(TURLER),
                          format_func=lambda k: t("tum_turler") if k == "hepsi" else TURLER[k],
                          label_visibility="collapsed")
tarihler = {"hepsi": t("tum_tarihler"), "bugun": t("bugun"), "7": t("son_7_gun"), "30": t("son_30_gun")}
tarih_filtre = f4.selectbox(t("tarih"), list(tarihler), format_func=tarihler.get, label_visibility="collapsed")

if kayitlar.empty:
    st.info(t("kayit_yok"), icon=":material/info:")
else:
    if arama:
        aranan = arama.lower()
        kayitlar = kayitlar[kayitlar["baslik"].str.lower().str.contains(aranan, regex=False)
                            | kayitlar["metin"].fillna("").str.lower().str.contains(aranan, regex=False)]
    if tur_filtre != "hepsi":
        kayitlar = kayitlar[kayitlar["tur"] == tur_filtre]
    if tarih_filtre == "bugun":
        kayitlar = kayitlar[kayitlar["zaman"].dt.date == datetime.now().date()]
    elif tarih_filtre in ("7", "30"):
        kayitlar = kayitlar[kayitlar["zaman"] >= datetime.now() - timedelta(days=int(tarih_filtre))]

    if sira == "yeni":
        kayitlar = kayitlar.sort_values("zaman", ascending=False)
    elif sira == "eski":
        kayitlar = kayitlar.sort_values("zaman", ascending=True)
    else:
        kayitlar = kayitlar.sort_values("baslik", key=lambda s: s.str.lower(), ascending=(sira == "az"))

    st.caption(t("kayit_sayisi", n=len(kayitlar)))
    for _, k in kayitlar.iterrows():
        baslik_satiri = f"{k['zaman']:%d.%m.%Y %H:%M}  ·  {TURLER.get(k['tur'], k['tur'])}  ·  {k['baslik']}"
        with st.expander(baslik_satiri, icon=TUR_IKON.get(k["tur"])):
            if pd.notna(k["ruh_hali"]):
                st.caption(f"{t('ruh_hali')}: {tx(ayarlar.RUH_HALI_SECENEKLERI[int(k['ruh_hali'])])}")
            if isinstance(k["metin"], str) and k["metin"]:
                st.write(k["metin"])
            yol = k["dosya_yolu"]
            if yol and os.path.exists(yol):
                if k["tur"] == "ses":
                    uzanti = yol.rsplit(".", 1)[-1].lower()
                    st.audio(yol, format={"mp3": "audio/mpeg", "m4a": "audio/mp4", "ogg": "audio/ogg",
                                          "webm": "audio/webm"}.get(uzanti, "audio/wav"))
                elif k["tur"] == "video":
                    st.video(yol)
            elif yol:
                st.warning(t("dosya_bulunamadi"))
            if st.button(t("sil"), key=f"sil_{k['id']}", icon=":material/delete:"):
                veritabani.gunluk_sil(int(k["id"]))
                st.rerun()
