"""
POLARIS — ASTRA'nın yapay zekası (Gemini ekranı gibi).

Boş sohbet: sayfanın ortasında logo, "Nereden başlayalım?", yazma kutusu ve altında Sohbet / Görev.
Sohbet başlayınca: mesajlar ortada (senin mesajın sağda balon içinde, Polaris'in cevabı düz metin),
yazma kutusu ekranın altında sabit; altında Sohbet / Görev ve küçük bir uyarı yazısı.
Yazma kutusunun solundaki + ile ses, video, belge ve görsel eklenir.
"""
import html as html_kacis
import mimetypes

import streamlit as st

import arayuz
import veritabani
import yapay_zeka
from arayuz import html
from ceviri import t

profil = veritabani.profil_getir()
anahtar = veritabani.gemini_anahtari()
model = yapay_zeka.etkin_model(veritabani.ayar("gemini_model"))
gecmis = veritabani.sohbet_gecmisi()

EK_TURLERI = ["png", "jpg", "jpeg", "webp", "pdf", "txt", "md", "csv", "docx",
              "mp3", "wav", "m4a", "ogg", "webm", "mp4", "mov"]
EN_FAZLA_EK = 18 * 1024 * 1024
GENISLIK = 760  # Polaris'in sohbet alanı genişliği (piksel); her şey sayfanın tam ortasında

st.markdown("""
<style>
.polaris-sahne {text-align:center; padding:13vh 0 22px 0; position:relative;}
.polaris-sahne:before {content:""; position:absolute; left:50%; top:55%; width:1000px; height:620px;
    transform:translate(-50%,-50%); pointer-events:none; z-index:-1;
    background:radial-gradient(ellipse at center, #1b2f6e 0%, #0f1a40 40%, transparent 70%);}
.polaris-baslik {font-size:2.4rem; font-weight:400; color:#e8edf7; margin-top:16px;}
.polaris-alt {color:#8aa0b8; font-size:.95rem; margin-top:8px;}
.balon-sag {display:flex; justify-content:flex-end; margin:18px 0 6px 0;}
.balon-sag div {background:#1f2733; color:#e8edf7; padding:10px 18px; border-radius:20px; max-width:75%;
    font-size:.98rem; line-height:1.5; white-space:pre-wrap;}
.polaris-cevap-ust {display:flex; align-items:center; gap:10px; margin:14px 0 2px 0; color:#8aa0b8;
    font-size:.8rem; font-weight:700; letter-spacing:.12em;}
.polaris-uyari {text-align:center; color:#64748b; font-size:.75rem; margin-top:4px;}
[data-testid="stChatInput"] {border-radius:28px !important;}
/* sohbet alanı, yazma kutusu, Sohbet/Görev ve uyarı yazısı: aynı genişlikte ve sayfanın ortasında */
.st-key-polaris_orta, .st-key-polaris_mesajlar, .st-key-polaris_alt {
    width:100%; max-width:GENISLIKpx; margin-left:auto !important; margin-right:auto !important;}
.st-key-polaris_giris, .st-key-polaris_alt [data-testid="stChatInput"],
.st-key-polaris_orta [data-testid="stChatInput"] {width:100% !important; max-width:GENISLIKpx;
    margin-left:auto !important; margin-right:auto !important;}
.st-key-polaris_mod, .st-key-polaris_mod > div {display:flex; justify-content:center; width:100%;}
.st-key-polaris_mod [data-testid="stButtonGroup"] {justify-content:center; margin:0 auto;}
[data-testid="stBottomBlockContainer"] {display:flex; flex-direction:column; align-items:center;}
</style>
""".replace("GENISLIK", str(GENISLIK)), unsafe_allow_html=True)


def mod_secici():
    """Yazma kutusunun altında, tam ortada Sohbet / Görev seçimi."""
    secim = st.segmented_control(t("mod"), ["sohbet", "gorev"], default="sohbet", key="polaris_mod",
                                 format_func=lambda m: t("mod_sohbet") if m == "sohbet" else t("mod_gorev"),
                                 label_visibility="collapsed")
    return secim == "gorev"


def kullanici_balonu(metin: str):
    html(f'<div class="balon-sag"><div>{html_kacis.escape(metin)}</div></div>')


def polaris_cevabi(metin: str):
    html(f'<div class="polaris-cevap-ust">{arayuz.logo_img(22)}POLARIS</div>')
    st.markdown(metin)


def mesaj_gonder(metin: str, dosyalar, gorev_modu: bool, alan):
    """Mesajı (ve ekleri) Polaris'e gönderir, cevabı ekrana yazar ve kaydeder."""
    ekler, ek_adlari, toplam = [], [], 0
    for f in dosyalar or []:
        veri = f.getvalue()
        toplam += len(veri)
        if toplam > EN_FAZLA_EK:
            st.warning(t("ek_cok_buyuk", ad=f.name))
            continue
        tip = f.type or mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        ekler.append((veri, tip))
        ek_adlari.append(f.name)
        veritabani.dosya_kaydet(veri, f.name.rsplit(".", 1)[-1])
    gosterilen = (metin or "") + (f"\n[{t('ekler')}: {', '.join(ek_adlari)}]" if ek_adlari else "")
    with alan:
        kullanici_balonu(gosterilen)
        with st.spinner(t("dusunuyor")):
            durum = arayuz.guncel_durum()
            cevap, _ = yapay_zeka.cevap_ver(metin, gecmis[-20:], profil, durum["degerlendirme"], durum["ruh"],
                                            veritabani.ayar("ortam"), anahtar, model, durum["radyasyon"],
                                            ekler=ekler, gorev_modu=gorev_modu)
        polaris_cevabi(cevap)
    veritabani.sohbet_ekle("user", gosterilen)
    veritabani.sohbet_ekle("model", cevap)


bekleyen = st.session_state.pop("bekleyen_soru", None)  # başka sayfadan gelen soru (ör. "Polaris ile konuş")

# ---------------------------------------------------------------
# BOŞ SOHBET: her şey sayfanın ortasında
# ---------------------------------------------------------------
if not gecmis and not bekleyen:
    with st.container(key="polaris_orta"):
        html(f'<div class="polaris-sahne">{arayuz.logo_img(64)}'
             f'<div class="polaris-baslik">{t("polaris_karsilama_baslik")}</div>'
             f'<div class="polaris-alt">{t("polaris_karsilama_alt", ad=profil["ad"])}</div></div>')
        giris = st.chat_input(t("polaris_yaz"), accept_file="multiple", file_type=EK_TURLERI, key="polaris_giris")
        gorev_modu = mod_secici()
        html(f'<div class="polaris-uyari">{t("polaris_uyari")}'
             f'{" · " + t("mod_cevrimdisi_aciklama") if not anahtar else ""}</div>')
        alan = st.container()
    if giris:
        mesaj_gonder(giris.text, giris.files, gorev_modu, alan)
        st.rerun()

# ---------------------------------------------------------------
# SOHBET VAR: mesajlar ortada, yazma kutusu ekranın altında
# ---------------------------------------------------------------
else:
    with st.container(key="polaris_mesajlar"):
        ust_sol, ust_sag = st.columns([4, 1], vertical_alignment="center")
        with ust_sol:
            html(f'<div class="marka">{arayuz.logo_img(30)}<div><div class="marka-ad" style="font-size:.95rem">'
                 f'POLARIS</div><div class="marka-alt">'
                 f'{t("mod_cevrimici_kisa") if anahtar else t("mod_cevrimdisi")}</div></div></div>')
        with ust_sag:
            if st.button(t("yeni_sohbet"), icon=":material/add_comment:", type="tertiary"):
                veritabani.sohbeti_temizle()
                st.rerun()
        for mesaj in gecmis:
            if mesaj["rol"] == "user":
                kullanici_balonu(mesaj["metin"])
            else:
                polaris_cevabi(mesaj["metin"])
        alan = st.container()
        html('<div style="height:90px"></div>')  # son mesaj alttaki kutunun arkasında kalmasın

    # Yazma kutusu + Sohbet/Görev + uyarı: ekranın altında sabit ve ortalı
    # Yeni Streamlit sürümlerinde adı st.bottom; eski sürümlerde st._bottom
    alt = st.bottom if hasattr(st, "bottom") else getattr(st, "_bottom", None)
    if alt is not None:
        with alt:
            with st.container(key="polaris_alt"):
                giris = st.chat_input(t("polaris_yaz"), accept_file="multiple", file_type=EK_TURLERI,
                                      key="polaris_giris")
                gorev_modu = mod_secici()
                html(f'<div class="polaris-uyari">{t("polaris_uyari")}</div>')
    else:  # çok eski Streamlit sürümü
        gorev_modu = mod_secici()
        giris = st.chat_input(t("polaris_yaz"), accept_file="multiple", file_type=EK_TURLERI, key="polaris_giris")

    if bekleyen:
        mesaj_gonder(bekleyen, [], gorev_modu, alan)
    elif giris:
        mesaj_gonder(giris.text, giris.files, gorev_modu, alan)
