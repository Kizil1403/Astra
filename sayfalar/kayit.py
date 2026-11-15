"""
KAYIT — İlk açılış.
1) Dil seçme ekranı: logo + "Dilinizi seçin" + bütün diller büyük düğmeler halinde.
2) Kısa kayıt anketi (seçilen dilde). Bilgiler veritabanındaki 'profil' tablosuna kaydedilir.
"""
import streamlit as st

import arayuz
import veritabani
from arayuz import html
from ceviri import t, DILLER

# ---------------------------------------------------------------
# 1) DİL SEÇİMİ — kayıt anketinden önce, bir kez
# ---------------------------------------------------------------
if not st.session_state.get("dil_secildi"):
    st.markdown("""
<style>
  [data-testid="stSidebar"] {display:none !important;}
  .dil-sahne {text-align:center; padding:6vh 0 26px 0; position:relative;}
  .dil-sahne:before {content:""; position:absolute; left:50%; top:45%; width:900px; height:520px;
      transform:translate(-50%,-50%); pointer-events:none; z-index:-1;
      background:radial-gradient(ellipse at center, #13285a 0%, #0b1530 40%, transparent 70%);}
  .dil-ad {margin-top:22px; color:#f1f5f9; font-size:2.2rem; font-weight:800; letter-spacing:.5em; padding-left:.5em;}
  .dil-baslik {margin-top:26px; color:#e2e8f0; font-size:1.25rem; font-weight:600;}
  .dil-alt {margin-top:6px; color:#7f95b3; font-size:.9rem; letter-spacing:.04em;}
  .st-key-dil_dugmeleri button {height:64px; width:100%; font-size:1.05rem; border-radius:10px;}
</style>""", unsafe_allow_html=True)
    html(f'<div class="dil-sahne">{arayuz.logo_img(110)}'
         f'<div class="dil-ad">ASTRA</div>'
         f'<div class="dil-baslik">Dilinizi seçin · Choose your language</div>'
         f'<div class="dil-alt">Elige tu idioma · Выберите язык · Choisissez votre langue · Sprache wählen</div></div>')

    _, orta, _ = st.columns([1, 3, 1])
    with orta:
        with st.container(key="dil_dugmeleri"):
            kodlar = list(DILLER)
            for i in range(0, len(kodlar), 4):
                for sutun, kod in zip(st.columns(4), kodlar[i:i + 4]):
                    yerel_ad, turkce_ad = DILLER[kod]
                    if sutun.button(yerel_ad, key=f"dil_sec_{kod}", help=turkce_ad,
                                    type="primary" if kod == st.session_state.get("dil", "tr") else "secondary"):
                        st.session_state["dil"] = kod
                        veritabani.ayar_kaydet("dil", kod)
                        st.session_state["dil_secildi"] = True
                        st.rerun()
    st.stop()

# ---------------------------------------------------------------
# 2) KAYIT ANKETİ
# ---------------------------------------------------------------
_, orta, _ = st.columns([1, 2.4, 1])
with orta:
    sol, sag = st.columns([4, 1], vertical_alignment="center")
    with sol:
        html(arayuz.marka_html())
    with sag:
        arayuz.dil_secici()
    if st.button(t("dil_soru"), icon=":material/arrow_back:", type="tertiary", key="dil_ekranina_don"):
        st.session_state["dil_secildi"] = False
        st.rerun()
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
