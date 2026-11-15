"""
ARAYÜZ — Bütün sayfaların ortak parçaları: tema (CSS), ikonlar, kartlar, üst bar.
"""
import base64
import os
from datetime import date, datetime

import streamlit as st

import ayarlar
import saglik_motoru
import veritabani
from ceviri import t, tx, DIL_ADLARI

# ---------------------------------------------------------------
# TEMA
# ---------------------------------------------------------------
CSS = """
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1500px;}
header[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {background:#0a1120; border-right:1px solid #1c2a40;}
section[data-testid="stSidebar"] {width:124px !important; min-width:124px !important; max-width:124px !important;}
section[data-testid="stSidebar"] > div {width:124px !important;}
[data-testid="stSidebarUserContent"] {padding:0.5rem 0 1rem 0 !important;}
section[data-testid="stSidebar"] .stButton {display:flex; justify-content:center;}
section[data-testid="stSidebar"] .stButton button {width:76px; height:58px; min-height:58px; padding:0;
    border-radius:6px; display:flex; align-items:center; justify-content:center;}
section[data-testid="stSidebar"] .stButton button [data-testid="stIconMaterial"] {font-size:30px;}
section[data-testid="stSidebar"] .stButton {margin-bottom:4px;}
section[data-testid="stSidebar"] .stButton button[kind="tertiary"] {color:#64748b;}
section[data-testid="stSidebar"] .stButton button[kind="tertiary"]:hover {color:#e2e8f0; background:#13233a;}
.menu-bosluk {height:32vh;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#1c2a40 !important; border-radius:6px;}
iframe[title="st.iframe"] {pointer-events:none;}
.marka {display:flex; align-items:center; gap:14px;}
.marka-logo {width:40px; height:40px; border:1px solid #2b6cb0; border-radius:4px; display:flex;
             align-items:center; justify-content:center; background:#0d1a2e;}
.marka-ad {font-weight:800; letter-spacing:.32em; font-size:1.15rem; color:#f1f5f9;}
.marka-rozet {font-size:.62rem; font-weight:700; letter-spacing:.12em; color:#93c5fd; border:1px solid #2b6cb0;
              padding:1px 6px; border-radius:3px; margin-left:8px; vertical-align:middle;}
.marka-alt {font-size:.66rem; letter-spacing:.18em; color:#64748b; margin-top:2px;}
.profil {display:flex; align-items:center; justify-content:flex-end; gap:12px;}
.profil-ad {font-weight:700; font-size:.9rem; color:#f1f5f9; text-align:right;}
.profil-unvan {font-size:.72rem; color:#8aa0b8; text-align:right;}
.avatar {width:38px; height:38px; border-radius:50%; border:1px solid #3b82f6; background:#0f2747;
         display:flex; align-items:center; justify-content:center; font-weight:700; font-size:.8rem; color:#dbeafe;}
.cevrimici {font-size:.75rem; color:#94a3b8;}
.cevrimici:before {content:""; display:inline-block; width:7px; height:7px; border-radius:50%;
                   background:#22d3ee; margin-right:7px; box-shadow:0 0 6px #22d3ee;}
.ust-yazi {color:#22d3ee; font-size:.70rem; letter-spacing:.16em; text-transform:uppercase; font-weight:600;}
.ust-yazi:before {content:""; display:inline-block; width:22px; height:1px; background:#22d3ee;
                  vertical-align:middle; margin-right:10px;}
.sayfa-baslik {font-size:2.1rem; font-weight:400; color:#f8fafc; margin:4px 0 2px 0; line-height:1.2;}
.sayfa-baslik b {font-weight:800;}
.sayfa-alt {color:#8aa0b8; font-size:.92rem; margin-bottom:6px;}
.bolum-ust {color:#8aa0b8; font-size:.68rem; letter-spacing:.16em; text-transform:uppercase; font-weight:600;}
.bolum-baslik {font-size:1.08rem; font-weight:700; color:#f1f5f9; margin:2px 0 8px 0;}
.mkart {background:#0c1524; border:1px solid #1c2a40; border-radius:4px; padding:14px 16px; margin-bottom:12px;
        min-height:132px;}
.mkart-ust {display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;}
.mikon {width:30px; height:30px; background:#13233a; border-radius:3px; display:flex; align-items:center;
        justify-content:center;}
.mdurum {font-size:.64rem; font-weight:800; letter-spacing:.12em;}
.metiket {font-size:.66rem; color:#8aa0b8; letter-spacing:.14em; text-transform:uppercase;}
.mdeger {font-size:1.9rem; font-weight:700; color:#f8fafc; line-height:1.2;}
.mbirim {font-size:.78rem; color:#8aa0b8; font-weight:400; margin-left:5px;}
.mnormal {font-size:.70rem; color:#64748b; margin-top:2px;}
.uyari {background:#0c1524; border:1px solid #1c2a40; border-radius:4px; padding:10px 14px; margin-bottom:8px;
        font-size:.92rem; color:#e2e8f0;}
.detay {background:#0c1524; border:1px solid #1c2a40; border-radius:4px; padding:12px 16px; margin-bottom:10px;
        font-size:.92rem; color:#e2e8f0; line-height:1.55;}
.etiket {display:inline-block; padding:2px 8px; border-radius:3px; font-size:.64rem; font-weight:800;
         letter-spacing:.1em; border:1px solid;}
.nokta {display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:8px; vertical-align:middle;}
.kutu {background:#0a1220; border:1px solid #1c2a40; border-radius:4px; padding:10px; text-align:center;}
.kutu-ust {font-size:.62rem; color:#8aa0b8; letter-spacing:.12em; text-transform:uppercase;}
.kutu-deger {font-size:1.0rem; font-weight:700; color:#f1f5f9;}
.radyasyon {width:120px; height:120px; border-radius:50%; border:1px solid #2b4a6f; margin:10px auto;
            display:flex; flex-direction:column; align-items:center; justify-content:center;
            background:radial-gradient(circle,#0f223b 0%,#0a1424 70%); box-shadow:0 0 30px #0b3b6b55;}
.buyuk-sayi {font-size:2.2rem; font-weight:800; color:#60a5fa; line-height:1;}
.gri {color:#8aa0b8; font-size:.85rem;}
</style>
"""


LOGO_YOLU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_kucuk.png")


def logo_img(boyut: int = 40) -> str:
    """Logoyu HTML içinde göstermek için <img> etiketi."""
    try:
        with open(LOGO_YOLU, "rb") as f:
            veri = base64.b64encode(f.read()).decode()
        return (f'<img src="data:image/png;base64,{veri}" width="{boyut}" height="{boyut}" '
                f'style="border-radius:{boyut // 4}px;box-shadow:0 0 14px #3b82f655">')
    except OSError:
        return ikon("nabiz", "#60a5fa", boyut // 2)


def marka_html(rozet: str = "") -> str:
    rozet_html = f'<span class="marka-rozet">{rozet}</span>' if rozet else ""
    return (f'<div class="marka">{logo_img(40)}<div>'
            f'<div class="marka-ad">ASTRA{rozet_html}</div>'
            f'<div class="marka-alt">{t("marka_alt")}</div></div></div>')


def avatar_html(bas_harfler: str, boyut: int = 38) -> str:
    """Profil fotoğrafı yüklendiyse fotoğraf, yoksa baş harfler."""
    yol = veritabani.profil_foto_yolu()
    if yol:
        with open(yol, "rb") as f:
            veri = base64.b64encode(f.read()).decode()
        return (f'<img src="data:image/jpeg;base64,{veri}" width="{boyut}" height="{boyut}" '
                f'style="border-radius:50%;object-fit:cover;border:1px solid #3b82f6">')
    return (f'<div class="avatar" style="width:{boyut}px;height:{boyut}px">{bas_harfler}</div>')


def stil_uygula():
    st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------
# İKONLAR (basit çizgi ikonlar, emoji yerine)
# ---------------------------------------------------------------
_IKON_YOLLARI = {
    "kalp": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2'
            'A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "damla": '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15'
             'a7 7 0 0 0 7 7z"/>',
    "ruzgar": '<path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2"/><path d="M9.6 4.6A2 2 0 1 1 11 8H2"/>'
              '<path d="M12.6 19.4A2 2 0 1 0 14 16H2"/>',
    "termometre": '<path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/>',
    "beyin": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "ay": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "egzersiz": '<path d="M6 5v14M18 5v14M3 9v6M21 9v6M6 12h12"/>',
    "nabiz": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "kitap": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5v14z"/><path d="M8 7h8M8 11h6"/>',
    "telefon": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2'
               ' 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3'
               'a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "tik": '<path d="M20 6 9 17l-5-5"/>',
    "kalkan": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "radyasyon": '<circle cx="12" cy="12" r="2"/><path d="M12 10 9 4.8a8 8 0 0 1 6 0Z"/>'
                 '<path d="m13.7 13 3 5.2a8 8 0 0 0 3-5.2Z"/><path d="m10.3 13-3 5.2a8 8 0 0 1-3-5.2Z"/>',
}


def ikon(ad: str, renk: str = "#7dd3fc", boyut: int = 16) -> str:
    return (f'<svg width="{boyut}" height="{boyut}" viewBox="0 0 24 24" fill="none" stroke="{renk}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{_IKON_YOLLARI[ad]}</svg>')


# ---------------------------------------------------------------
# KÜÇÜK PARÇALAR
# ---------------------------------------------------------------
def html(icerik: str):
    st.markdown(icerik, unsafe_allow_html=True)


def nokta(durum_veya_renk: str) -> str:
    renk = ayarlar.RENKLER.get(durum_veya_renk, durum_veya_renk)
    return f'<span class="nokta" style="background:{renk};box-shadow:0 0 6px {renk}"></span>'


def etiket(durum: str) -> str:
    renk = ayarlar.RENKLER[durum]
    return (f'<span class="etiket" style="color:{renk};border-color:{renk}55;background:{renk}14">'
            f'{tx(ayarlar.DURUM_YAZILARI[durum])}</span>')


def bolum_basligi(ust: str, baslik: str = None):
    html(f'<div class="bolum-ust">{ust}</div>' + (f'<div class="bolum-baslik">{baslik}</div>' if baslik else ""))


def sayfa_basligi(ust: str, baslik: str, alt: str = None):
    html(f'<div class="ust-yazi">{ust}</div><div class="sayfa-baslik">{baslik}</div>'
         + (f'<div class="sayfa-alt">{alt}</div>' if alt else ""))


def metrik_karti(d: dict) -> str:
    return (f'<div class="mkart" style="border-left:2px solid {d["renk"]}">'
            f'<div class="mkart-ust"><div class="mikon">{ikon(d["ikon"], d["renk"])}</div>'
            f'<span class="mdurum" style="color:{d["renk"]}">{d["durum_yazisi"]}</span></div>'
            f'<div class="metiket">{d["ad"]}</div>'
            f'<div class="mdeger">{d["deger_yazi"]}<span class="mbirim">{d["birim"]}</span></div>'
            f'<div class="mnormal">{t("normal")}: {d["normal_yazi"]} {d["birim"]}</div></div>')


def aralik_yazisi(saniye: int) -> str:
    return f"{saniye} {t('sn')}" if saniye < 60 else f"{saniye // 60} {t('dk')}"


def selamlama() -> str:
    saat = datetime.now().hour
    if 5 <= saat < 12:
        return t("gunaydin")
    if 12 <= saat < 18:
        return t("iyi_gunler")
    if 18 <= saat < 23:
        return t("iyi_aksamlar")
    return t("iyi_geceler")


def gorev_gunu(profil: dict) -> int:
    try:
        return (date.today() - date.fromisoformat(profil["gorev_baslangic"])).days + 1
    except Exception:
        return 1


def unvan_yazisi(profil: dict) -> str:
    return tx(ayarlar.UNVAN_CEVIRI.get(profil.get("unvan"), profil.get("unvan") or ""))


def seviye_bilgisi(puan: int):
    seviye = puan // ayarlar.SEVIYE_PUANI + 1
    unvan = tx(ayarlar.SEVIYE_UNVANLARI[min(seviye - 1, len(ayarlar.SEVIYE_UNVANLARI) - 1)])
    return seviye, unvan


# ---------------------------------------------------------------
# GÜNCEL DURUM (birçok sayfada kullanılır)
# ---------------------------------------------------------------
def guncel_durum() -> dict:
    olcum = veritabani.son_olcum()
    degerlendirme = saglik_motoru.olcumu_degerlendir(olcum)
    ruh_kaydi = veritabani.bugunku_ruh_hali()
    ruh = saglik_motoru.ruh_halini_degerlendir(ruh_kaydi)
    profil = veritabani.profil_getir() or {}
    radyasyon = saglik_motoru.radyasyon_degerlendir(gorev_gunu(profil), veritabani.ayar("ortam"))
    return {
        "olcum": olcum, "degerlendirme": degerlendirme, "ruh_kaydi": ruh_kaydi, "ruh": ruh,
        "radyasyon": radyasyon,
        "bolgeler": saglik_motoru.bolge_durumlari(degerlendirme, ruh, radyasyon),
        "puan": saglik_motoru.saglik_puani(degerlendirme, ruh, radyasyon),
        "uyarilar": saglik_motoru.uyarilar(degerlendirme, ruh, radyasyon),
    }


# ---------------------------------------------------------------
# DİL SEÇİMİ
# ---------------------------------------------------------------
def _dil_kaydet():
    veritabani.ayar_kaydet("dil", st.session_state.dil)


def dil_secici():
    """Sağ üstteki dil seçimi: düğmeye basınca 'Hangi dili seçmek istiyorsunuz?' diye sorar.
    Listeden seçilebilir ya da kutuya yazarak aranabilir (örneğin 'alm' yazınca Almanca çıkar)."""
    from ceviri import DILLER
    mevcut = st.session_state.get("dil", "tr")
    with st.popover(f":material/translate: {DILLER.get(mevcut, (mevcut,))[0]}"):
        st.selectbox(t("dil_soru"), options=list(DILLER), key="dil", on_change=_dil_kaydet,
                     format_func=lambda k: f"{DILLER[k][0]}  ·  {DILLER[k][1]}",
                     help=t("dil_yardim"))


# ---------------------------------------------------------------
# ÜST BAR: marka | çevrimiçi | bildirimler | dil | profil
# ---------------------------------------------------------------
def ust_bar(profil: dict, bildirim_listesi: list):
    ortam = ayarlar.ORTAMLAR[veritabani.ayar("ortam")]
    c_marka, c_durum, c_bildirim, c_dil, c_profil = st.columns([3.6, 1.3, 1.25, 1.05, 2.3],
                                                               vertical_alignment="center")
    with c_marka:
        html(marka_html(ortam["kisa"]))
    with c_durum:
        html(f'<div class="cevrimici">{t("sistem_cevrimici") if veritabani.ayar("canli") == "1" else t("saat_beklemede")}</div>')
    with c_bildirim:
        with st.popover(f":material/notifications: {t('bildirimler')} ({len(bildirim_listesi)})"):
            html(f'<div class="bolum-ust">{t("bugun_yapilacaklar")}</div>')
            st.caption(t("bildirim_tikla"))
            if not bildirim_listesi:
                st.caption(t("bildirim_yok"))
            renkler = {"kirmizi": "red", "sari": "orange", "bilgi": "blue"}
            for i, b in enumerate(bildirim_listesi):
                if st.button(f":{renkler[b['durum']]}[●] {b['metin']}", key=f"bildirim_{i}", type="tertiary"):
                    tur, deger = b["hedef"]
                    if tur == "gorev":
                        st.switch_page("sayfalar/gorevler.py")
                    elif tur == "bolge":
                        st.session_state["secili_bolge"] = deger
                        st.switch_page("sayfalar/anlik_degerler.py")
                    else:
                        st.switch_page(deger)
    with c_dil:
        dil_secici()
    with c_profil:
        bas_harfler = ((profil.get("ad") or " ")[0] + (profil.get("soyad") or " ")[0]).upper().strip()
        html(f'<div class="profil"><div><div class="profil-ad">{profil.get("ad", "")} {profil.get("soyad", "")}</div>'
             f'<div class="profil-unvan">{unvan_yazisi(profil)} · {ortam["kisa"]}</div></div>'
             f'{avatar_html(bas_harfler)}</div>')
    html('<div style="border-bottom:1px solid #1c2a40;margin:10px 0 18px 0"></div>')


# ---------------------------------------------------------------
# PROFİL FORMU (kayıt anketi ve ayarlar sayfasında ortak)
# ---------------------------------------------------------------
def profil_formu(mevcut: dict, buton_yazisi: str, form_adi: str):
    """Profil bilgilerini soran form. Gönderilirse bilgileri sözlük olarak döndürür, yoksa None."""
    m = mevcut or {}
    with st.form(form_adi, border=False):
        bolum_basligi(t("kimlik_bilgileri"))
        c1, c2 = st.columns(2)
        ad = c1.text_input(t("ad") + " *", value=m.get("ad", ""))
        soyad = c2.text_input(t("soyad") + " *", value=m.get("soyad", ""))
        c3, c4 = st.columns(2)
        unvan_index = ayarlar.UNVANLAR.index(m["unvan"]) if m.get("unvan") in ayarlar.UNVANLAR else 0
        unvan = c3.selectbox(t("unvan"), ayarlar.UNVANLAR, index=unvan_index,
                             format_func=lambda u: tx(ayarlar.UNVAN_CEVIRI[u]))
        cinsiyetler = ["Kadın", "Erkek"]
        cinsiyet = c4.radio(t("cinsiyet"), cinsiyetler, horizontal=True,
                            index=cinsiyetler.index(m.get("cinsiyet", "Kadın")),
                            format_func=lambda c: t("kadin") if c == "Kadın" else t("erkek"))

        bolum_basligi(t("fiziksel_bilgiler"))
        c5, c6, c7, c8 = st.columns(4)
        dogum_yili = c5.number_input(t("dogum_yili"), 1940, 2010, int(m.get("dogum_yili") or 1985))
        boy = c6.number_input(t("boy_cm"), 140, 210, int(m.get("boy") or 170))
        kilo = c7.number_input(t("kilo_kg"), 40.0, 140.0, float(m.get("kilo") or 65.0), step=0.5)
        kan_index = ayarlar.KAN_GRUPLARI.index(m["kan_grubu"]) if m.get("kan_grubu") in ayarlar.KAN_GRUPLARI else 0
        kan_grubu = c8.selectbox(t("kan_grubu"), ayarlar.KAN_GRUPLARI, index=kan_index,
                                 format_func=lambda k: t("bilinmiyor") if k == "Bilinmiyor" else k)

        bolum_basligi(t("saglik_gecmisi"))
        st.caption(t("saglik_gecmisi_aciklama"))
        kronik = st.text_input(t("kronik_hastalik"), value=m.get("kronik_hastalik") or "",
                               placeholder=t("kronik_ornek"))
        c9, c10 = st.columns(2)
        ilaclar = c9.text_input(t("ilaclar"), value=m.get("ilaclar") or "", placeholder=t("yok_ise_bos"))
        alerjiler = c10.text_input(t("alerjiler"), value=m.get("alerjiler") or "", placeholder=t("yok_ise_bos"))

        bolum_basligi(t("gorev_bilgileri"))
        c11, c12 = st.columns(2)
        ortam_listesi = list(ayarlar.ORTAMLAR)
        ortam = c11.selectbox(t("gorev_ortami"), ortam_listesi,
                              index=ortam_listesi.index(veritabani.ayar("ortam")),
                              format_func=lambda k: tx(ayarlar.ORTAMLAR[k]["ad"]))
        try:
            baslangic_degeri = date.fromisoformat(m["gorev_baslangic"])
        except Exception:
            baslangic_degeri = date.today()
        baslangic = c12.date_input(t("gorev_baslangic"), value=baslangic_degeri, format="DD.MM.YYYY")

        if st.form_submit_button(buton_yazisi, type="primary", icon=":material/check:"):
            if not ad.strip() or not soyad.strip():
                st.error(t("ad_soyad_gerekli"))
                return None
            veritabani.ayar_kaydet("ortam", ortam)
            return {"ad": ad.strip(), "soyad": soyad.strip(), "unvan": unvan, "cinsiyet": cinsiyet,
                    "dogum_yili": int(dogum_yili), "boy": int(boy), "kilo": float(kilo), "kan_grubu": kan_grubu,
                    "kronik_hastalik": kronik.strip(), "ilaclar": ilaclar.strip(), "alerjiler": alerjiler.strip(),
                    "gorev_baslangic": baslangic.isoformat()}
    return None


# ---------------------------------------------------------------
# KÜÇÜK ÖZET KARTI (sparkline'lı) — bölge panelinde kullanılır
# ---------------------------------------------------------------
def rozet(durum: str) -> str:
    renk = ayarlar.RENKLER[durum]
    return (f'<span style="display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;'
            f'background:{renk}22;color:{renk};font-size:.75rem;font-weight:700">'
            f'<span style="width:7px;height:7px;border-radius:50%;background:{renk}"></span>'
            f'{tx(ayarlar.DURUM_YAZILARI[durum]).capitalize()}</span>')


def sparkline(degerler, renk: str = "#5eead4") -> str:
    degerler = [float(v) for v in degerler][-60:]
    if len(degerler) < 2:
        return '<div style="height:42px"></div>'
    en_az, en_cok = min(degerler), max(degerler)
    aralik = (en_cok - en_az) or 1
    n = len(degerler) - 1
    noktalar = " ".join(f"{i / n * 200:.1f},{38 - (v - en_az) / aralik * 32:.1f}" for i, v in enumerate(degerler))
    return (f'<svg viewBox="0 0 200 42" preserveAspectRatio="none" style="width:100%;height:42px;display:block">'
            f'<polyline points="{noktalar}" fill="none" stroke="{renk}" stroke-width="2" '
            f'vector-effect="non-scaling-stroke"/></svg>')


def mini_kart(d: dict, degerler, alt_yazi: str) -> str:
    return (f'<div style="background:#0a1220;border:1px solid #1c2a40;border-radius:10px;padding:14px 16px;'
            f'margin-bottom:12px">'
            f'<div class="metiket">{d["ad"]}</div>'
            f'<div style="font-size:1.7rem;font-weight:700;color:#f8fafc;margin:2px 0 6px 0;font-family:monospace">'
            f'{d["deger_yazi"]}<span style="font-size:.8rem;color:#8aa0b8;margin-left:8px">{d["birim"]}</span></div>'
            f'{sparkline(degerler)}'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px">'
            f'<span style="font-family:monospace;font-size:.8rem;color:#8aa0b8">{alt_yazi}</span>'
            f'{rozet(d["durum"])}</div></div>')


def not_kutusu(metin: str, renk: str = "#1c2a40") -> str:
    return (f'<div style="background:#111b2d;border-radius:8px;padding:14px 16px;margin-top:6px;'
            f'border-left:3px solid {renk};color:#e2e8f0;font-size:.93rem;line-height:1.55">{metin}</div>')


# ---------------------------------------------------------------
# GÖREV ORTAMI KUTULARI + CANLI DÜNYA SAATİ
# Saat tarayıcıda her saniye ilerler (Dünya'daki yerel saat ve UTC).
# ---------------------------------------------------------------
def ortam_kutulari_html(kutular: list, saat_basligi: str) -> str:
    kutu_stil = ("flex:1;background:#0a1220;border:1px solid #1c2a40;border-radius:4px;padding:12px;"
                 "text-align:center")
    ust_stil = "font-size:10px;color:#8aa0b8;letter-spacing:.12em;text-transform:uppercase"
    deger_stil = "font-size:17px;font-weight:700;color:#f1f5f9;margin-top:4px"
    icerik = "".join(f'<div style="{kutu_stil}"><div style="{ust_stil}">{ad}</div>'
                     f'<div style="{deger_stil}">{deger}</div></div>' for ad, deger in kutular)
    icerik += (f'<div style="{kutu_stil};border-color:#1f6fff66"><div style="{ust_stil}">{saat_basligi}</div>'
               f'<div id="saat" style="{deger_stil};font-family:monospace"></div>'
               f'<div id="utc" style="font-size:10px;color:#64748b;margin-top:2px;font-family:monospace"></div></div>')
    return f"""
<style>html,body{{margin:0;padding:0;overflow:hidden;background:transparent}}</style>
<div style="display:flex;gap:10px;font-family:sans-serif">{icerik}</div>
<script>
function guncelle() {{
  const s = new Date();
  const iki = n => String(n).padStart(2, '0');
  document.getElementById('saat').textContent = iki(s.getHours()) + ':' + iki(s.getMinutes()) + ':' + iki(s.getSeconds());
  document.getElementById('utc').textContent = 'UTC ' + iki(s.getUTCHours()) + ':' + iki(s.getUTCMinutes());
}}
guncelle(); if (!DURAKLADI) setInterval(guncelle, 1000);
</script>"""


def dunya_saati_html(baslik: str) -> str:
    """Başlıktaki canlı Dünya saati (tarayıcıda her saniye ilerler)."""
    return f"""
<style>html,body{{margin:0;padding:0;overflow:hidden;background:transparent}}</style>
<div style="font-family:sans-serif;background:#0c1524;border:1px solid #1f6fff99;border-radius:8px;
            padding:0 14px;display:flex;align-items:center;justify-content:space-between;height:58px;
            box-sizing:border-box;margin:1px">
  <div>
    <div style="font-size:10px;color:#8aa0b8;letter-spacing:.14em;text-transform:uppercase">{baslik}</div>
    <div id="tarih" style="font-size:11px;color:#64748b;margin-top:2px"></div>
  </div>
  <div style="text-align:right">
    <div id="saat" style="font:700 22px monospace;color:#f1f5f9;line-height:1"></div>
    <div id="utc" style="font:10px monospace;color:#64748b;margin-top:3px"></div>
  </div>
</div>
<script>
const iki = n => String(n).padStart(2, '0');
function guncelle() {{
  const s = new Date();
  document.getElementById('saat').textContent = iki(s.getHours()) + ':' + iki(s.getMinutes()) + ':' + iki(s.getSeconds());
  document.getElementById('utc').textContent = 'UTC ' + iki(s.getUTCHours()) + ':' + iki(s.getUTCMinutes());
  document.getElementById('tarih').textContent = iki(s.getDate()) + '.' + iki(s.getMonth() + 1) + '.' + s.getFullYear();
}}
guncelle(); if (!DURAKLADI) setInterval(guncelle, 1000);
</script>"""


def geri_sayim_html(baslangic: float, sure: int, etiket: str, bitti_yazisi: str, duraklatildi: bool = False) -> str:
    """Antrenman için canlı geri sayım (örneğin 90:00 -> 00:00)."""
    return f"""
<style>html,body{{margin:0;padding:0;overflow:hidden;background:transparent}}</style>
<div style="font-family:sans-serif;display:flex;align-items:center;gap:14px;height:50px;padding:0 4px">
  <div style="flex:1">
    <div style="font-size:10px;color:#8aa0b8;letter-spacing:.14em;text-transform:uppercase">{etiket}</div>
    <div style="height:6px;background:#1c2a40;border-radius:3px;margin-top:6px;overflow:hidden">
      <div id="cubuk" style="height:6px;width:0;background:#22c55e;border-radius:3px"></div></div>
  </div>
  <div id="sayac" style="font:700 26px monospace;color:{"#facc15" if duraklatildi else "#f1f5f9"};min-width:96px;
       text-align:right"></div>
</div>
<script>
const BAS = {baslangic * 1000:.0f}, SURE = {sure} * 1000, DURAKLADI = {"true" if duraklatildi else "false"};
const iki = n => String(n).padStart(2, '0');
function guncelle() {{
  const kalan = Math.max(0, SURE - (Date.now() - BAS));
  const dk = Math.floor(kalan / 60000), sn = Math.floor((kalan % 60000) / 1000);
  document.getElementById('sayac').textContent = kalan > 0 ? iki(dk) + ':' + iki(sn) : '{bitti_yazisi}';
  document.getElementById('cubuk').style.width = (100 * (1 - kalan / SURE)).toFixed(1) + '%';
}}
guncelle(); if (!DURAKLADI) setInterval(guncelle, 1000);
</script>"""


# ---------------------------------------------------------------
# AÇILIŞ (GEÇİŞ) EKRANI — kayıttan sonra, ana sayfa açılmadan önce
# ---------------------------------------------------------------
ACILIS_SURESI = 3.2  # saniye


def acilis_ekrani(ad: str, ilk_kez: bool = False):
    """Tam ekran: logo parlayarak belirir, ASTRA yazısı ve karşılama gelir, yükleme çubuğu dolar."""
    st.markdown(f"""
<style>
  [data-testid="stSidebar"], header[data-testid="stHeader"] {{display:none !important;}}
  @keyframes logoGel {{ 0% {{opacity:0; transform:scale(.55) rotate(-8deg); filter:blur(8px)}}
                        60% {{opacity:1; transform:scale(1.06) rotate(0); filter:blur(0)}}
                        100% {{opacity:1; transform:scale(1)}} }}
  @keyframes parilti {{ 0%,100% {{box-shadow:0 0 40px #3b82f655, 0 0 90px #1d4ed833}}
                        50% {{box-shadow:0 0 70px #60a5fa99, 0 0 160px #3b82f655}} }}
  @keyframes yaziGel {{ from {{opacity:0; transform:translateY(14px); letter-spacing:.2em}}
                        to {{opacity:1; transform:translateY(0); letter-spacing:.55em}} }}
  @keyframes belir {{ from {{opacity:0}} to {{opacity:1}} }}
  @keyframes dolum {{ from {{width:0}} to {{width:100%}} }}
  @keyframes yildiz {{ 0%,100% {{opacity:.25}} 50% {{opacity:1}} }}
  .acilis {{position:fixed; inset:0; z-index:999999; display:flex; flex-direction:column; align-items:center;
            justify-content:center; background:radial-gradient(ellipse at 50% 45%, #13285a 0%, #070d18 62%, #03060c 100%);
            font-family:sans-serif;}}
  .acilis-yildizlar span {{position:absolute; width:2px; height:2px; border-radius:50%; background:#cfe3ff;
            animation:yildiz 2.4s ease-in-out infinite;}}
  .acilis-logo {{border-radius:34px; animation:logoGel 1.1s cubic-bezier(.2,.8,.2,1) both,
            parilti 2.2s ease-in-out .9s infinite;}}
  .acilis-ad {{margin-top:34px; color:#f1f5f9; font-size:2.6rem; font-weight:800; letter-spacing:.55em;
            padding-left:.55em; animation:yaziGel 1s ease-out .55s both;}}
  .acilis-alt {{margin-top:10px; color:#7f95b3; font-size:.78rem; letter-spacing:.32em;
            animation:belir .8s ease-out 1s both;}}
  .acilis-merhaba {{margin-top:30px; color:#cbd5e1; font-size:1.15rem; animation:belir .8s ease-out 1.35s both;}}
  .acilis-cubuk {{margin-top:26px; width:220px; height:3px; border-radius:2px; background:#1c2a40; overflow:hidden;
            animation:belir .4s ease-out 1.3s both;}}
  .acilis-cubuk div {{height:3px; background:linear-gradient(90deg,#1f6fff,#60a5fa); border-radius:2px;
            animation:dolum {ACILIS_SURESI - 1.3:.1f}s ease-in-out 1.3s both;}}
</style>
<div class="acilis">
  <div class="acilis-yildizlar">{_yildizlar()}</div>
  {logo_img(150).replace('style="', 'class="acilis-logo" style="', 1)}
  <div class="acilis-ad">ASTRA</div>
  <div class="acilis-alt">{t("marka_alt")}</div>
  <div class="acilis-merhaba">{t("hos_geldin" if ilk_kez else "tekrar_hos_geldin", ad=ad)}</div>
  <div class="acilis-cubuk"><div></div></div>
</div>
""", unsafe_allow_html=True)


def _yildizlar(adet: int = 70) -> str:
    """Arka planda rastgele parıldayan küçük yıldızlar."""
    import random
    rnd = random.Random(7)
    return "".join(
        f'<span style="left:{rnd.uniform(0, 100):.1f}%;top:{rnd.uniform(0, 100):.1f}%;'
        f'animation-delay:{rnd.uniform(0, 2.4):.2f}s;transform:scale({rnd.choice([1, 1, 1.5, 2])})"></span>'
        for _ in range(adet))
