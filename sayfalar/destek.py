"""
GÜVENLİK VE YARDIM — Ruh sağlığı desteği.
Acil destek, günlük ruh hali kontrolü, kişisel öneriler, rahatlama egzersizleri ve konu rehberleri.
"""
import streamlit as st
import streamlit.components.v1 as components

import arayuz
import ayarlar
import grafikler
import saglik_motoru
import veritabani
from arayuz import html
from ceviri import t, tx

arayuz.sayfa_basligi(t("destek_ust"), t("destek_baslik"), t("destek_alt"))
durum = arayuz.guncel_durum()

# ---------------------------------------------------------------
# EVE BAĞLAN — astronotların en sık yaşadığı duygu: aileyi ve Dünya'yı özlemek
# ---------------------------------------------------------------
with st.container(border=True):
    html(f'<div class="bolum-ust" style="color:#60a5fa">{t("ozlem_ust")}</div>'
         f'<div class="bolum-baslik">{t("ozlem_baslik")}</div><div class="gri">{t("ozlem_aciklama")}</div>')
    st.write("")
    o1, o2, o3 = st.columns(3)
    if o1.button(t("ozlem_aile"), icon=":material/video_call:", key="ozlem_aile", type="primary"):
        veritabani.destek_talebi_ekle("aile")
        veritabani.gorev_tamamla("aile", 30)
        st.success(t("talep_gonderildi", ad=t("ozlem_aile")), icon=":material/check_circle:")
    if o2.button(t("ozlem_mesaj"), icon=":material/mic:", key="ozlem_mesaj"):
        st.session_state["gunluk_tur"] = "ses"
        st.switch_page("sayfalar/gunluk.py")
    if o3.button(t("ozlem_polaris"), icon=":material/smart_toy:", key="ozlem_polaris"):
        st.session_state["bekleyen_soru"] = t("hazir_2")
        st.switch_page("sayfalar/asistan.py")
    st.caption(t("ozlem_dunya"))

st.write("")

# ---------------------------------------------------------------
# ACİL DESTEK
# ---------------------------------------------------------------
with st.container(border=True):
    html(f'<div class="bolum-ust" style="color:#f87171">{t("acil_ust")}</div>'
         f'<div class="bolum-baslik">{t("acil_baslik")}</div><div class="gri">{t("acil_aciklama")}</div>')
    st.write("")
    b1, b2, b3, b4 = st.columns(4)
    talepler = [
        (b1, "doktor", t("talep_doktor"), ":material/medical_services:"),
        (b2, "psikolog", t("talep_psikolog"), ":material/psychology:"),
        (b3, "ekip", t("talep_ekip"), ":material/groups:"),
        (b4, "aile", t("talep_aile"), ":material/call:"),
    ]
    for sutun, tur, ad, ikon in talepler:
        if sutun.button(ad, icon=ikon, key=f"talep_{tur}", type="primary" if tur == "doktor" else "secondary"):
            veritabani.destek_talebi_ekle(tur)
            if tur == "aile":
                veritabani.gorev_tamamla("aile", 30)
            st.success(t("talep_gonderildi", ad=ad), icon=":material/check_circle:")

st.write("")

# ---------------------------------------------------------------
# RUH HALİ KONTROLÜ ve KİŞİSEL ÖNERİLER
# ---------------------------------------------------------------
sol, sag = st.columns(2, gap="large")
with sol:
    with st.container(border=True):
        arayuz.bolum_basligi(t("kontrol_ust"), t("kontrol_baslik"))
        st.caption(t("kontrol_aciklama"))
        with st.form("ruh_hali_formu", border=False):
            ruh_hali = st.select_slider(t("soru_ruh"), options=[1, 2, 3, 4, 5], value=3,
                                        format_func=lambda x: tx(ayarlar.RUH_HALI_SECENEKLERI[x]))
            stres = st.slider(t("soru_stres"), 1, 10, 4)
            enerji = st.slider(t("soru_enerji"), 1, 5, 3)
            yalnizlik = st.slider(t("soru_yalnizlik"), 1, 5, 2)
            notu = st.text_area(t("soru_not"), height=80)
            if st.form_submit_button(t("kaydet"), type="primary", icon=":material/save:"):
                veritabani.ruh_hali_ekle(ruh_hali, stres, enerji, yalnizlik, notu)
                if veritabani.gorev_tamamla("ruh_hali", 30):
                    st.session_state["bildirim"] = t("ruh_kaydedildi_puan")
                else:
                    st.session_state["bildirim"] = t("ruh_kaydedildi")
                st.rerun()

with sag:
    with st.container(border=True):
        r = durum["ruh"]
        arayuz.bolum_basligi(t("oneri_ust"), t("oneri_baslik"))
        html(f'<div class="detay" style="border-left:3px solid {ayarlar.RENKLER[r["durum"]]}">'
             f'{arayuz.nokta(r["durum"])}<b>{r["baslik"]}</b><br>{r["ne_yapmali"]}</div>')
        oneriler = saglik_motoru.kisisel_oneriler(durum["degerlendirme"], durum["ruh_kaydi"])
        for i, oneri in enumerate(oneriler, 1):
            html(f'<div style="display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #1c2a40">'
                 f'<div style="color:#60a5fa;font-weight:800;min-width:18px">{i}</div>'
                 f'<div style="color:#e2e8f0">{oneri}</div></div>')

    gecmis = veritabani.ruh_hali_gecmisi(14)
    if len(gecmis) > 0:
        with st.container(border=True):
            st.plotly_chart(grafikler.ruh_hali_grafigi(
                gecmis, {"ruh_hali": t("grafik_ruh"), "enerji": t("grafik_enerji"), "stres": t("grafik_stres")},
                t("son_14_gun")), config={"displayModeBar": False})

st.write("")

# ---------------------------------------------------------------
# REGL DÖNGÜSÜ TAKİBİ — yalnızca kadın profillerde
# ---------------------------------------------------------------
if (veritabani.profil_getir() or {}).get("cinsiyet") == "Kadın":
    import dongu_takibi
    dongu_takibi.goster()
    st.write("")

# ---------------------------------------------------------------
# RAHATLAMA EGZERSİZLERİ
# ---------------------------------------------------------------
arayuz.bolum_basligi(t("egzersiz_ust"), t("egzersiz_baslik"))
nefes, *egz_sutunlar = st.columns([1, 1, 1, 1])
with nefes:
    with st.container(border=True):
        html(f'<div class="bolum-baslik" style="font-size:.95rem">{t("nefes_rehberi")}</div>')
        components.html(f"""
<div style="height:210px;display:flex;flex-direction:column;align-items:center;justify-content:center;
            font-family:sans-serif;color:#cbd5e1;background:#0c1524">
  <div id="d" style="width:70px;height:70px;border-radius:50%;background:radial-gradient(circle,#38bdf8,#1e3a8a);
       box-shadow:0 0 30px #38bdf866;transition:all 4s ease-in-out"></div>
  <div id="y" style="margin-top:26px;font-size:15px;font-weight:600;letter-spacing:.05em"></div>
</div>
<script>
const d=document.getElementById('d'), y=document.getElementById('y');
const adim=[["{t('nefes_al')}",4000,140],["{t('nefes_tut')}",7000,140],["{t('nefes_ver')}",8000,70]];
let i=0;
function dongu(){{const [yazi,sure,boy]=adim[i]; y.textContent=yazi; d.style.transitionDuration=(sure/1000)+'s';
  d.style.width=boy+'px'; d.style.height=boy+'px'; i=(i+1)%3; setTimeout(dongu,sure);}}
dongu();
</script>""", height=215)
        if "nefes" in veritabani.bugun_tamamlanan_gorevler():
            st.caption(t("yapildi"))
        elif st.button(t("bitirdim") + " (+20)", key="destek_nefes_bitti", icon=":material/check:"):
            veritabani.gorev_tamamla("nefes", 20)
            st.session_state["bildirim"] = t("puan_kazandin", gorev=t("nefes_rehberi"), puan=20)
            st.rerun()
for sutun, egz in zip(egz_sutunlar, ayarlar.EGZERSIZLER):
    with sutun:
        with st.container(border=True):
            html(f'<div class="bolum-baslik" style="font-size:.95rem">{tx(egz["ad"])}</div>'
                 f'<div class="gri">{tx(egz["sure"])}</div>')
            for i, adim in enumerate(tx(egz["adimlar"]), 1):
                html(f'<div style="font-size:.86rem;padding:3px 0;color:#cbd5e1">'
                     f'<span style="color:#60a5fa;font-weight:700">{i}.</span> {adim}</div>')

st.write("")

# ---------------------------------------------------------------
# KONU REHBERLERİ
# ---------------------------------------------------------------
arayuz.bolum_basligi(t("konular_ust"), t("konular_baslik"))
for konu in ayarlar.KONULAR:
    with st.expander(tx(konu["ad"]), icon=":material/psychology:"):
        st.write(tx(konu["aciklama"]))
        st.markdown(f"**{t('ne_yapabilirsin')}:**")
        for adim in tx(konu["adimlar"]):
            st.markdown(f"- {adim}")

talepler_df = veritabani.destek_talepleri()
if len(talepler_df) > 0:
    with st.expander(t("gecmis_talepler"), icon=":material/history:"):
        adlar = {"doktor": t("talep_doktor"), "psikolog": t("talep_psikolog"), "ekip": t("talep_ekip"),
                 "aile": t("talep_aile")}
        for _, s in talepler_df.iterrows():
            st.markdown(f"- {s['zaman'][:16]} · {adlar.get(s['tur'], s['tur'])}")
