"""
GÖREVLER — Etkileşimli günlük görevler, puan, seviye ve sağlık serisi.
Bildirimlerden bir göreve tıklanınca bu sayfa açılır ve o görev en üstte vurgulanır.
"""
import time
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

import arayuz
import ayarlar
import grafikler
import saat_simulatoru
import veritabani
from arayuz import html
from ceviri import t, tx

ortam_kodu = veritabani.ayar("ortam")
ANTRENMAN_SURESI = 90 * 60  # saniye


def antrenman_gecen() -> float:
    """Antrenmanda geçen toplam süre (saniye): duraklatmadan önceki süre + şu anki çalışma süresi."""
    gecen = float(veritabani.ayar("antrenman_gecen") or 0)
    baslangic = float(veritabani.ayar("antrenman_baslangic") or 0)
    return gecen + (time.time() - baslangic if baslangic else 0)


def antrenmani_bitir(tamamlandi: bool):
    for anahtar in ("antrenman_baslangic", "antrenman_gecen", "antrenman_durum"):
        veritabani.ayar_kaydet(anahtar, "")
    veritabani.ayar_kaydet("senaryo", "normal")
    if tamamlandi and veritabani.gorev_tamamla("egzersiz", 50):
        st.session_state["bildirim"] = t("antrenman_tamam")
    st.rerun()


# süre dolduysa antrenman kendiliğinden tamamlanır
if veritabani.ayar("antrenman_durum") == "calisiyor" and antrenman_gecen() >= ANTRENMAN_SURESI:
    antrenmani_bitir(tamamlandi=True)

olcum = veritabani.son_olcum()
yapilanlar = veritabani.bugun_tamamlanan_gorevler()

# Otomatik tamamlananlar: saat 90 dk egzersiz gördüyse
if olcum["egzersiz"] >= 90 and "egzersiz" not in yapilanlar:
    veritabani.gorev_tamamla("egzersiz", next(g["puan"] for g in ayarlar.GOREVLER if g["kod"] == "egzersiz"))
    st.session_state["bildirim"] = t("egzersiz_tamamlandi")
    st.rerun()


def tamamla(gorev):
    if veritabani.gorev_tamamla(gorev["kod"], gorev["puan"]):
        st.session_state["bildirim"] = t("puan_kazandin", gorev=tx(gorev["ad"]), puan=gorev["puan"])
    st.rerun()


def geri_al(gorev):
    veritabani.gorev_geri_al(gorev["kod"])
    st.rerun()


KART_YUKSEKLIGI = 262  # bütün görev kartları aynı yükseklikte (simetrik düzen)


def kart_basligi(g, yapildi):
    """Kartın üst kısmı: ikon, görev adı, puan, açıklama. Her kartta aynı yükseklikte."""
    renk = ayarlar.RENKLER["yesil"] if yapildi else "#60a5fa"
    ikon = arayuz.ikon("tik" if yapildi else g["ikon"], renk, 18)
    html(f'''
<div style="display:flex;align-items:center;gap:12px;height:40px">
  <div style="width:38px;height:38px;flex-shrink:0;border-radius:10px;display:flex;align-items:center;
              justify-content:center;background:{renk}1f;border:1px solid {renk}55">{ikon}</div>
  <div style="flex:1;min-width:0;font-weight:700;font-size:.95rem;white-space:nowrap;overflow:hidden;
              text-overflow:ellipsis;color:{"#94a3b8" if yapildi else "#f1f5f9"};
              {"text-decoration:line-through" if yapildi else ""}">{tx(g["ad"])}</div>
  <div style="flex-shrink:0;padding:3px 10px;border-radius:999px;font-size:.75rem;font-weight:800;
              background:{"#22c55e22" if yapildi else "#1f6fff22"};color:{"#4ade80" if yapildi else "#93c5fd"}">
    +{g["puan"]}</div>
</div>
<div style="height:38px;margin:8px 0 10px 0;font-size:.8rem;color:#8aa0b8;line-height:1.35;overflow:hidden;
            display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">{tx(g["aciklama"])}</div>
''')


def gorev_karti(g, anahtar_eki=""):
    yapildi = g["kod"] in yapilanlar
    k = anahtar_eki
    with st.container(border=True, height=KART_YUKSEKLIGI):
        kart_basligi(g, yapildi)
        tur = g["etkilesim"]

        if tur == "su":
            ml = veritabani.bugun_su_ml()
            toplam_bardak = ayarlar.SU_HEDEF_ML // ayarlar.BARDAK_ML
            dolu = min(ml // ayarlar.BARDAK_ML, toplam_bardak)
            bardaklar = "".join(
                f'<svg width="16" height="22" viewBox="0 0 16 22" style="margin-right:4px">'
                f'<path d="M1 1h14l-2 20H3z" fill="{"#38bdf8" if i < dolu else "none"}" stroke="#38bdf8" '
                f'stroke-width="1.4" opacity="{1 if i < dolu else .45}"/></svg>' for i in range(toplam_bardak))
            html(f'<div style="display:flex;align-items:center;justify-content:space-between;height:26px">'
                 f'<div style="display:flex">{bardaklar}</div>'
                 f'<span class="gri" style="font-size:.8rem">{ml} / {ayarlar.SU_HEDEF_ML} ml</span></div>')
            html('<div style="height:10px"></div>')
            a, b, _ = st.columns([1, 1, 1.4], gap="small")
            if a.button(f"+{ayarlar.BARDAK_ML} ml", key=f"su_arti{k}", icon=":material/water_drop:",
                        type="primary"):
                if veritabani.su_ekle(ayarlar.BARDAK_ML) >= ayarlar.SU_HEDEF_ML and not yapildi:
                    tamamla(g)
                st.rerun()
            if b.button(f"-{ayarlar.BARDAK_ML} ml", key=f"su_eksi{k}", disabled=ml == 0):
                if veritabani.su_ekle(-ayarlar.BARDAK_ML) < ayarlar.SU_HEDEF_ML and yapildi:
                    geri_al(g)
                st.rerun()

        elif tur == "olcum":
            if yapildi:
                st.caption(t("olculen_nabiz", n=f"{olcum['nabiz']:.0f}"))
                if st.button(t("geri_al"), key=f"g_geri_{g['kod']}{k}", icon=":material/undo:"):
                    geri_al(g)
            elif st.button(t("simdi_olc"), key=f"g_olc{k}", icon=":material/ecg_heart:", type="primary"):
                saat_simulatoru.olcum_al_ve_kaydet(veritabani.ayar("senaryo"), ortam_kodu)
                tamamla(g)

        elif tur == "egzersiz":
            durum = veritabani.ayar("antrenman_durum")  # "" | "calisiyor" | "duraklatildi"
            if yapildi:
                st.progress(1.0, text=t("antrenman_tamam"))
            elif durum:
                # 90 dakikadan geriye sayan sayaç; duraklatılınca olduğu yerde durur
                calisiyor = durum == "calisiyor"
                components.html(arayuz.geri_sayim_html(
                    time.time() - antrenman_gecen(), ANTRENMAN_SURESI,
                    t("kalan_sure") if calisiyor else t("antrenman_duraklatildi"), t("antrenman_tamam"),
                    duraklatildi=not calisiyor), height=58)
                b1, b2 = st.columns(2, gap="small")
                if calisiyor:
                    if b1.button(t("antrenman_duraklat"), key=f"g_antr_dur{k}", icon=":material/pause_circle:"):
                        veritabani.ayar_kaydet("antrenman_gecen", antrenman_gecen())
                        veritabani.ayar_kaydet("antrenman_baslangic", "")
                        veritabani.ayar_kaydet("antrenman_durum", "duraklatildi")
                        veritabani.ayar_kaydet("senaryo", "normal")
                        st.rerun()
                elif b1.button(t("antrenman_devam"), key=f"g_antr_devam{k}", icon=":material/play_circle:",
                               type="primary"):
                    veritabani.ayar_kaydet("antrenman_baslangic", time.time())
                    veritabani.ayar_kaydet("antrenman_durum", "calisiyor")
                    veritabani.ayar_kaydet("senaryo", "egzersiz")
                    st.rerun()
                if b2.button(t("antrenman_bitir"), key=f"g_antr_bitir{k}", icon=":material/stop_circle:"):
                    antrenmani_bitir(tamamlandi=antrenman_gecen() >= ANTRENMAN_SURESI)
            else:
                st.progress(0.0, text=f"90:00 {t('dk')}")
                if st.button(t("antrenman_baslat"), key=f"g_antr{k}", icon=":material/fitness_center:",
                             type="primary"):
                    veritabani.ayar_kaydet("antrenman_baslangic", time.time())
                    veritabani.ayar_kaydet("antrenman_gecen", 0)
                    veritabani.ayar_kaydet("antrenman_durum", "calisiyor")
                    veritabani.ayar_kaydet("senaryo", "egzersiz")
                    saat_simulatoru.olcum_al_ve_kaydet("egzersiz", ortam_kodu)
                    st.rerun()

        elif tur == "nefes":
            if yapildi:
                if st.button(t("geri_al"), key=f"g_geri_{g['kod']}{k}", icon=":material/undo:"):
                    geri_al(g)
            elif st.session_state.get("nefes_acik"):
                components.html(f"""
<div style="height:62px;display:flex;align-items:center;justify-content:center;gap:16px;
            font-family:sans-serif;color:#cbd5e1;background:#0c1524">
  <div style="width:62px;height:62px;display:flex;align-items:center;justify-content:center">
    <div id="d" style="width:22px;height:22px;border-radius:50%;background:radial-gradient(circle,#38bdf8,#1e3a8a);
         box-shadow:0 0 18px #38bdf866;transition:all 4s ease-in-out"></div></div>
  <div id="y" style="font-size:14px;font-weight:600;width:90px"></div>
</div>
<script>
const d=document.getElementById('d'), y=document.getElementById('y');
const adim=[["{t('nefes_al')}",4000,58],["{t('nefes_tut')}",7000,58],["{t('nefes_ver')}",8000,22]];
let i=0;
function dongu(){{const [yazi,sure,boy]=adim[i]; y.textContent=yazi; d.style.transitionDuration=(sure/1000)+'s';
  d.style.width=boy+'px'; d.style.height=boy+'px'; i=(i+1)%3; setTimeout(dongu,sure);}}
dongu();
</script>""", height=64)
                if st.button(t("bitirdim"), key=f"g_nefes_bitti{k}", type="primary", icon=":material/check:"):
                    st.session_state["nefes_acik"] = False
                    tamamla(g)
            elif st.button(t("baslat"), key=f"g_nefes{k}", icon=":material/air:", type="primary"):
                st.session_state["nefes_acik"] = True
                st.rerun()

        elif tur == "sayfa_destek":
            if yapildi:
                st.caption(t("yapildi"))
            elif st.button(t("formu_ac"), key=f"g_ruh{k}", icon=":material/arrow_forward:", type="primary"):
                st.switch_page("sayfalar/destek.py")

        elif tur == "sayfa_gunluk":
            if yapildi:
                st.caption(t("yapildi"))
            elif st.button(t("gunluge_git"), key=f"g_gunluk{k}", icon=":material/arrow_forward:", type="primary"):
                st.switch_page("sayfalar/gunluk.py")

        elif tur == "onay":
            isaretli = st.toggle(t("yaptim"), value=yapildi, key=f"g_onay_{g['kod']}{k}")
            if isaretli and not yapildi:
                tamamla(g)
            if not isaretli and yapildi:
                geri_al(g)


def ozet_karti():
    """Görev sayısı tekse ızgarayı tamamlayan kart: bugünün özeti."""
    kalan = [g for g in ayarlar.GOREVLER if g["kod"] not in yapilanlar]
    with st.container(border=True, height=KART_YUKSEKLIGI):
        html(f'<div style="display:flex;align-items:center;gap:12px;height:40px">'
             f'<div style="width:38px;height:38px;border-radius:10px;display:flex;align-items:center;'
             f'justify-content:center;background:#a78bfa1f;border:1px solid #a78bfa55">'
             f'{arayuz.ikon("kalkan", "#a78bfa", 18)}</div>'
             f'<div style="font-weight:700;font-size:.95rem;color:#f1f5f9">{t("bugun_ozet")}</div></div>'
             f'<div style="margin-top:14px;font-size:2rem;font-weight:800;color:#a78bfa">'
             f'+{veritabani.bugun_kazanilan_puan()} <span style="font-size:.85rem;color:#8aa0b8">{t("puan")}</span></div>'
             f'<div class="gri" style="margin-top:6px">{t("kalan_gorev", n=len(kalan))}</div>')


# ---------------------------------------------------------------
# ÜST KISIM: ilerleme halkası, puan, seviye, seri
# ---------------------------------------------------------------
toplam = len(ayarlar.GOREVLER)
biten = len(yapilanlar)
yuzde = biten / toplam * 100
puan = veritabani.toplam_puan()
seviye, unvan = arayuz.seviye_bilgisi(puan)
seri = veritabani.seri_gun_sayisi()

arayuz.sayfa_basligi(t("rutin_ust"), t("gorevler_baslik"), t("bugun_kazanilan", n=veritabani.bugun_kazanilan_puan()))

k1, k2, k3, k4 = st.columns(4)
with k1:
    html(f'<div class="mkart" style="display:flex;align-items:center;gap:16px">'
         f'<div style="width:84px;height:84px;border-radius:50%;flex-shrink:0;'
         f'background:conic-gradient(#22c55e {yuzde}%, #1c2a40 0);display:flex;align-items:center;justify-content:center">'
         f'<div style="width:68px;height:68px;border-radius:50%;background:#0c1524;display:flex;align-items:center;'
         f'justify-content:center;font-weight:800;font-size:1.15rem;color:#f1f5f9">{biten}/{toplam}</div></div>'
         f'<div><div class="metiket">{t("bugun")}</div><div class="gri">{t("tamamlandi").capitalize()}</div></div></div>')
with k2:
    html(f'<div class="mkart"><div class="metiket">{t("gorev_puani")}</div>'
         f'<div class="mdeger" style="color:#60a5fa">{puan}</div>'
         f'<div class="mnormal">{t("bugun_kazanilan", n=veritabani.bugun_kazanilan_puan())}</div></div>')
with k3:
    html(f'<div class="mkart"><div class="metiket">{t("seviye")} {seviye}</div>'
         f'<div class="mdeger" style="font-size:1.25rem;margin:6px 0">{unvan}</div>'
         f'<div style="height:6px;background:#1c2a40;border-radius:3px;overflow:hidden">'
         f'<div style="height:6px;width:{(puan % ayarlar.SEVIYE_PUANI) / ayarlar.SEVIYE_PUANI * 100:.0f}%;'
         f'background:#60a5fa"></div></div>'
         f'<div class="mnormal" style="margin-top:6px">'
         f'{t("sonraki_seviye", n=ayarlar.SEVIYE_PUANI - puan % ayarlar.SEVIYE_PUANI)}</div></div>')
with k4:
    html(f'<div class="mkart"><div class="metiket">{t("saglik_serisi")}</div>'
         f'<div class="mdeger" style="color:#22c55e">{seri} <span class="mbirim">{t("gun")}</span></div>'
         f'<div class="mnormal">{t("seri_aciklama", n=seri)}</div></div>')

if biten == toplam and not st.session_state.get(f"kutlama_{date.today()}"):
    st.session_state[f"kutlama_{date.today()}"] = True
    st.balloons()
    st.success(t("hepsi_tamam"))

# ---------------------------------------------------------------
# TÜM GÖREVLER
# ---------------------------------------------------------------
st.write("")
arayuz.bolum_basligi(t("rutin_ust"), t("rutin_baslik"))
digerleri = list(ayarlar.GOREVLER)
kartlar = [lambda g=g: gorev_karti(g) for g in digerleri]
if len(kartlar) % 2:  # tek sayıdaysa son boşluğu özet kartı doldursun, ızgara simetrik kalsın
    kartlar.append(ozet_karti)
for i in range(0, len(kartlar), 2):
    for sutun, kart in zip(st.columns(2, gap="medium"), kartlar[i:i + 2]):
        with sutun:
            kart()

# ---------------------------------------------------------------
# PUAN GEÇMİŞİ
# ---------------------------------------------------------------
gecmis = veritabani.gunluk_puanlar(14)
if len(gecmis) > 1:
    with st.container(border=True):
        arayuz.bolum_basligi(t("son_14_gun").upper(), t("puan_gecmisi"))
        st.plotly_chart(grafikler.puan_grafigi(gecmis), config={"displayModeBar": False})
