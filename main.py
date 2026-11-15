"""
ASTRA — Astronot Sağlık İzleme Sistemi (ana dosya)

Çalıştırmak için terminale:   streamlit run main.py

Bu dosya:
 1) Veritabanını hazırlar
 2) İlk açılışta kayıt anketini gösterir
 3) Saatten canlı veri alır
 4) Üst barı (profil, bildirimler, dil) ve sol menüyü kurar
"""
import os

import streamlit as st

import arayuz
import ayarlar
import saat_simulatoru
import saglik_motoru
import veritabani
from ceviri import t

LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
st.set_page_config(page_title="Astra", page_icon=LOGO, layout="wide",
                   initial_sidebar_state="expanded")

# --- İnternetteki (bulut) sürüm: her ziyaretçiye ayrı veritabanı ---
# Streamlit Cloud'un gizli ayarlarında  bulut_modu = true  yazıyorsa açılır.
# Kimlik adres çubuğuna (?k=...) eklenir; sayfa yenilense de aynı kişi aynı verisini görür.
if veritabani.gizli_ayar("bulut_modu", False):
    import re
    import uuid
    kimlik = st.query_params.get("k", "")
    if not re.fullmatch(r"[a-f0-9]{12}", kimlik or ""):
        kimlik = uuid.uuid4().hex[:12]
        st.query_params["k"] = kimlik
    veritabani.kullanici_klasorunu_ayarla(kimlik)

veritabani.kur()

if "dil" not in st.session_state:
    st.session_state.dil = veritabani.ayar("dil")

arayuz.stil_uygula()

# --- Elle çevrilmemiş bir dil seçildiyse: bir kerelik otomatik çeviri (deep-translator) ---
import ceviri
if not ceviri.hazir_mi(st.session_state.dil) and not st.session_state.get(f"ceviri_hata_{st.session_state.dil}"):
    yer = st.empty()
    with yer.container():
        st.info(t("ceviri_hazirlaniyor", dil=ceviri.DIL_ADLARI.get(st.session_state.dil, st.session_state.dil)),
                icon=":material/translate:")
        cubuk = st.progress(0.0)
        try:
            ceviri.hazirla(st.session_state.dil, lambda oran: cubuk.progress(min(oran, 1.0)))
            if not ceviri.hazir_mi(st.session_state.dil):  # bir kısmı çevrilemediyse tekrar tekrar deneme
                st.session_state[f"ceviri_hata_{st.session_state.dil}"] = "baglanti"
        except ImportError:
            st.session_state[f"ceviri_hata_{st.session_state.dil}"] = "paket"
        except Exception:
            st.session_state[f"ceviri_hata_{st.session_state.dil}"] = "baglanti"
    yer.empty()
if st.session_state.get(f"ceviri_hata_{st.session_state.dil}"):
    st.warning(t("ceviri_paket_yok") if st.session_state[f"ceviri_hata_{st.session_state.dil}"] == "paket"
               else t("ceviri_baglanti_yok"), icon=":material/translate:")
st.logo(LOGO, icon_image=LOGO)

# --- 1) İlk açılış: kayıt anketi ---
profil = veritabani.profil_getir()
if profil is None:
    st.navigation([st.Page("sayfalar/kayit.py", title=t("kayit_menu"), icon=":material/person_add:")],
                  position="hidden").run()
    st.stop()

# --- Açılış ekranı: uygulama her açıldığında / tarayıcıda sayfa yenilendiğinde bir kez ---
# (Düğmelere basınca tekrar çıkmaz; yalnızca yeni bir oturum başladığında görünür.)
if not st.session_state.get("acilis_gosterildi"):
    import time as _zaman
    st.session_state["acilis_gosterildi"] = True
    ilk_kez = st.session_state.pop("acilis_ekrani", False)  # kayıttan hemen sonra mı?
    arayuz.acilis_ekrani(profil["ad"], ilk_kez=ilk_kez)
    _zaman.sleep(arayuz.ACILIS_SURESI)
    st.session_state["bildirim"] = t("hos_geldin" if ilk_kez else "tekrar_hos_geldin", ad=profil["ad"])
    st.rerun()  # ardından ana sayfa (ya da yenilenen sayfa) açılır

# --- 2) Saatten canlı veri (varsayılan: 3 dakikada bir) ---
aralik = int(veritabani.ayar("olcum_araligi"))
if veritabani.son_olcum() is None or (
        veritabani.ayar("canli") == "1" and saat_simulatoru.olcum_zamani_geldi_mi(aralik - 1)):
    saat_simulatoru.olcum_al_ve_kaydet(veritabani.ayar("senaryo"), veritabani.ayar("ortam"))

# Saat 90 dakika egzersiz gördüyse egzersiz görevi kendiliğinden tamamlanır
if veritabani.son_olcum()["egzersiz"] >= 90 and veritabani.gorev_tamamla(
        "egzersiz", next(g["puan"] for g in ayarlar.GOREVLER if g["kod"] == "egzersiz")):
    st.session_state["bildirim"] = t("egzersiz_tamamlandi")

# Antrenman sayacı 90 dakikayı doldurduysa egzersiz görevi tamamlanır
import time
_antrenman = float(veritabani.ayar("antrenman_baslangic") or 0)
_gecen = float(veritabani.ayar("antrenman_gecen") or 0) + (time.time() - _antrenman if _antrenman else 0)
if veritabani.ayar("antrenman_durum") == "calisiyor" and _gecen >= 90 * 60:
    for _a in ("antrenman_baslangic", "antrenman_gecen", "antrenman_durum"):
        veritabani.ayar_kaydet(_a, "")
    veritabani.ayar_kaydet("senaryo", "normal")
    if veritabani.gorev_tamamla("egzersiz", 50):
        st.session_state["bildirim"] = t("antrenman_tamam")

# Görev tamamlanınca gösterilecek bildirim (sayfa yenilendikten sonra)
if "bildirim" in st.session_state:
    st.toast(st.session_state.pop("bildirim"), icon=":material/stars:")

# --- 3) Üst bar ---
durum = arayuz.guncel_durum()
bildirim_listesi = saglik_motoru.bildirimler(durum["degerlendirme"], durum["ruh"],
                                             veritabani.bugun_tamamlanan_gorevler(), profil, veritabani.ayar)
arayuz.ust_bar(profil, bildirim_listesi)

# --- 4) Sol menü: yalnızca simgeler (üzerine gelince adı görünür) ---
sayfalar = [
    (st.Page("sayfalar/anlik_degerler.py", title=t("menu_anlik"), default=True), ":material/monitor_heart:"),
    (st.Page("sayfalar/gorevler.py", title=t("menu_gorevler")), ":material/task_alt:"),
    (st.Page("sayfalar/grafik_sayfasi.py", title=t("menu_grafik")), ":material/monitoring:"),
    (st.Page("sayfalar/destek.py", title=t("menu_destek")), ":material/health_and_safety:"),
    (st.Page("sayfalar/gunluk.py", title=t("menu_gunluk")), ":material/menu_book:"),
    (st.Page("sayfalar/asistan.py", title=t("menu_asistan")), ":material/smart_toy:"),
    (st.Page("sayfalar/ayarlar_sayfasi.py", title=t("menu_ayarlar")), ":material/settings:"),
]
secili_sayfa = st.navigation([p for p, _ in sayfalar], position="hidden")

with st.sidebar:
    for i, (sayfa, ikon) in enumerate(sayfalar):
        if i == len(sayfalar) - 1:  # Ayarlar en altta
            st.markdown('<div class="menu-bosluk"></div>', unsafe_allow_html=True)
        aktif = sayfa.title == secili_sayfa.title
        if st.button(ikon, key=f"menu_{i}", help=sayfa.title, type="primary" if aktif else "tertiary"):
            st.switch_page(sayfa)

secili_sayfa.run()
