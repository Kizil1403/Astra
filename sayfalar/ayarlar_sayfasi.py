"""
AYARLAR — Profil, görev ve canlı veri, bildirimler, yapay zeka, dil, veriler, hakkında.
"""
import streamlit as st

import arayuz
import ayarlar
import saat_simulatoru
import veritabani
import yapay_zeka
from ceviri import t, tx, DIL_ADLARI

arayuz.sayfa_basligi(t("ayarlar_ust"), t("ayarlar_baslik"))


def ayar_toggle(anahtar, yazi, yardim=None):
    eski = veritabani.ayar(anahtar) == "1"
    yeni = st.toggle(yazi, value=eski, help=yardim, key=f"ayar_{anahtar}")
    if yeni != eski:
        veritabani.ayar_kaydet(anahtar, "1" if yeni else "0")


sekmeler = st.tabs([t("sekme_profil"), t("sekme_gorev"), t("sekme_bildirim"), t("sekme_yz"), t("sekme_dil"),
                    t("sekme_veri"), t("sekme_hakkinda")])

# --- PROFİL ---
with sekmeler[0]:
    profil_simdiki = veritabani.profil_getir()
    arayuz.bolum_basligi(t("profil_foto_ust"))
    foto_sol, foto_sag = st.columns([1, 4], vertical_alignment="center")
    with foto_sol:
        bas_harfler = ((profil_simdiki.get("ad") or " ")[0] + (profil_simdiki.get("soyad") or " ")[0]).upper()
        arayuz.html(arayuz.avatar_html(bas_harfler, 96))
    with foto_sag:
        yeni_foto = st.file_uploader(t("profil_foto_yukle"), type=["png", "jpg", "jpeg", "webp"],
                                     key="profil_foto_yukleyici")
        b1, b2 = st.columns(2)
        if yeni_foto is not None and b1.button(t("profil_foto_kaydet"), icon=":material/save:", type="primary"):
            veritabani.profil_foto_kaydet(yeni_foto.getvalue())
            st.session_state["bildirim"] = t("kaydedildi")
            st.rerun()
        if veritabani.profil_foto_yolu() and b2.button(t("profil_foto_kaldir"), icon=":material/delete:"):
            veritabani.profil_foto_sil()
            st.rerun()
    st.divider()
    bilgi = arayuz.profil_formu(veritabani.profil_getir(), t("degisiklikleri_kaydet"), "profil_formu")
    if bilgi:
        veritabani.profil_kaydet(bilgi)
        st.session_state["bildirim"] = t("kaydedildi")
        st.rerun()

# --- GÖREV VE CANLI VERİ ---
with sekmeler[1]:
    ortam_listesi = list(ayarlar.ORTAMLAR)
    eski_ortam = veritabani.ayar("ortam")
    ortam = st.selectbox(t("gorev_ortami"), ortam_listesi, index=ortam_listesi.index(eski_ortam),
                         format_func=lambda k: tx(ayarlar.ORTAMLAR[k]["ad"]))
    if ortam != eski_ortam:
        veritabani.ayar_kaydet("ortam", ortam)
        st.rerun()
    st.caption(tx(ayarlar.ORTAMLAR[ortam]["not"]))
    st.divider()

    ayar_toggle("canli", t("canli_veri"), t("canli_veri_yardim"))
    eski_aralik = int(veritabani.ayar("olcum_araligi"))
    if eski_aralik not in ayarlar.OLCUM_ARALIKLARI:
        eski_aralik = ayarlar.VARSAYILAN_OLCUM_ARALIGI
    aralik = st.select_slider(t("olcum_araligi_ayar"), options=ayarlar.OLCUM_ARALIKLARI, value=eski_aralik,
                              format_func=arayuz.aralik_yazisi, help=t("olcum_araligi_yardim"))
    if aralik != eski_aralik:
        veritabani.ayar_kaydet("olcum_araligi", aralik)
    st.divider()

    arayuz.bolum_basligi(t("demo_ust"), t("demo_baslik"))
    st.caption(t("demo_aciklama"))
    senaryolar = list(ayarlar.SENARYOLAR)
    eski_senaryo = veritabani.ayar("senaryo")
    senaryo = st.selectbox(t("senaryo"), senaryolar, index=senaryolar.index(eski_senaryo),
                           format_func=lambda k: tx(ayarlar.SENARYOLAR[k]["ad"]))
    if senaryo != eski_senaryo:
        veritabani.ayar_kaydet("senaryo", senaryo)
    c1, c2 = st.columns(2)
    if c1.button(t("demo_veri_olustur"), icon=":material/history:"):
        with st.spinner(t("demo_veri_uretiliyor")):
            adet = saat_simulatoru.gecmis_veri_uret(14, veritabani.ayar("ortam"))
        st.success(t("demo_veri_hazir", n=adet))
    if c2.button(t("olcumleri_sifirla"), icon=":material/restart_alt:"):
        veritabani.olcumleri_sil()
        st.success(t("olcumler_silindi"))

# --- BİLDİRİMLER ---
with sekmeler[2]:
    st.caption(t("bildirim_ayar_aciklama"))
    ayar_toggle("bildirim_su", t("bildirim_su_ayar"))
    ayar_toggle("bildirim_gorev", t("bildirim_gorev_ayar"))
    ayar_toggle("bildirim_ruh", t("bildirim_ruh_ayar"))
    ayar_toggle("bildirim_ilac", t("bildirim_ilac_ayar"))
    if (veritabani.profil_getir() or {}).get("cinsiyet") == "Kadın":
        ayar_toggle("bildirim_dongu", t("bildirim_dongu_ayar"))

# --- YAPAY ZEKA (POLARIS) ---
with sekmeler[3]:
    st.markdown(t("yz_aciklama"))
    sunucu_anahtari = bool((veritabani.gizli_ayar("GEMINI_API_KEY") or "").strip())
    if sunucu_anahtari:  # internetteki sürüm: anahtar gizli ayarlardan gelir, burada gösterilmez
        st.success(t("anahtar_sunucuda"), icon=":material/lock:")
        anahtar = veritabani.gemini_anahtari()
    else:
        eski_anahtar = veritabani.ayar("gemini_anahtar")
        anahtar = st.text_input(t("api_anahtari"), value=eski_anahtar, type="password")
    eski_model = yapay_zeka.etkin_model(veritabani.ayar("gemini_model"))
    secenekler = yapay_zeka.MODEL_SECENEKLERI + ["diger"]
    secili = eski_model if eski_model in yapay_zeka.MODEL_SECENEKLERI else "diger"
    model_secimi = st.selectbox(t("model_adi"), secenekler, index=secenekler.index(secili),
                                format_func=lambda m: t("diger_model") if m == "diger" else m,
                                help=t("model_yardim"))
    model = (st.text_input(t("model_yaz"), value=eski_model if secili == "diger" else "")
             if model_secimi == "diger" else model_secimi)
    c1, c2 = st.columns(2)
    if c1.button(t("kaydet"), icon=":material/save:", key="yz_kaydet", type="primary"):
        if not sunucu_anahtari:
            veritabani.ayar_kaydet("gemini_anahtar", anahtar.strip())
        veritabani.ayar_kaydet("gemini_model", (model or yapay_zeka.VARSAYILAN_MODEL).strip())
        st.success(t("kaydedildi"))
    if c2.button(t("baglanti_test"), icon=":material/wifi_tethering:", key="yz_test"):
        if not anahtar.strip():
            st.error(t("anahtar_yok"))
        else:
            with st.spinner(t("baglanti_deneniyor")):
                basarili, mesaj, modeller = yapay_zeka.baglanti_testi(anahtar.strip(), (model or "").strip())
            if basarili:
                st.success(t("baglanti_basarili", mesaj=mesaj))
            else:
                st.error(t("baglanti_basarisiz"))
                st.code(mesaj)
                if modeller:
                    st.info(t("kullanilabilir_modeller") + " " + ", ".join(modeller))

# --- DİL ---
with sekmeler[4]:
    def _dil_ayardan():
        st.session_state.dil = st.session_state.dil_ayar
        veritabani.ayar_kaydet("dil", st.session_state.dil_ayar)

    from ceviri import DILLER
    diller = list(DILLER)
    st.selectbox(t("dil_soru"), diller, index=diller.index(st.session_state.get("dil", "tr")),
                 format_func=lambda k: f"{DILLER[k][0]}  ·  {DILLER[k][1]}", key="dil_ayar",
                 on_change=_dil_ayardan)
    st.caption(t("dil_aciklama"))

# --- VERİLER ---
with sekmeler[5]:
    tum = veritabani.tum_olcumler()
    st.download_button(t("tum_veriyi_indir"), tum.to_csv(index=False).encode("utf-8"),
                       file_name="astra_olcumler.csv", mime="text/csv", icon=":material/download:")
    st.divider()
    st.warning(t("hepsini_sil_uyari"), icon=":material/warning:")
    onay = st.checkbox(t("hepsini_sil_onay"))
    if st.button(t("hepsini_sil"), disabled=not onay, icon=":material/delete_forever:"):
        veritabani.her_seyi_sil()
        st.session_state.clear()
        st.rerun()

# --- HAKKINDA ---
with sekmeler[6]:
    st.markdown(t("hakkinda_metni"))
