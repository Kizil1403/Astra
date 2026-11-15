"""
ANLIK DEĞERLER — Ana sayfa.
Hareketli canlı nabız, anlık değerler ve normal aralıkları, vücut haritası (röntgen / termal),
bölge paneli (özet kartları + Uyarı/Kritik çizgili grafik), etkileşimli günlük görevler, görev ortamı.
"""
import random
from datetime import datetime, timedelta, date

import streamlit as st
import streamlit.components.v1 as components

import arayuz
import ayarlar
import grafikler
import monitor
import saat_simulatoru
import saglik_motoru
import veritabani
import vucut_cizimi
from arayuz import html
from ceviri import t, tx

profil = veritabani.profil_getir()
ortam_kodu = veritabani.ayar("ortam")
ortam = ayarlar.ORTAMLAR[ortam_kodu]
canli = veritabani.ayar("canli") == "1"
aralik = int(veritabani.ayar("olcum_araligi"))

# ---------------------------------------------------------------
# BAŞLIK
# ---------------------------------------------------------------
durum = arayuz.guncel_durum()
kalan_rutin = len(ayarlar.GOREVLER) - len(veritabani.bugun_tamamlanan_gorevler())
genel_durum = t("durum_stabil") if not durum["uyarilar"] else (
    t("durum_dikkat") if all(u["durum"] == "sari" for u in durum["uyarilar"]) else t("durum_acil"))

sol, saat, sag = st.columns([2.5, 1.05, 1.05], vertical_alignment="bottom", gap="small")
with sol:
    arayuz.sayfa_basligi(
        f"{t('gorev_gunu')} {arayuz.gorev_gunu(profil)} · {tx(ortam['ad'])}",
        f"{arayuz.selamlama()}, <b>{profil['ad']}.</b>",
        f"{genel_durum} {t('kalan_rutin', n=kalan_rutin)}",
    )
with saat:  # Dünya saati, Hızlı kontrol düğmesinin solunda ve aynı boyda (58 px)
    components.html(arayuz.dunya_saati_html(t("dunya_saati")), height=60)
with sag:
    if st.button(t("hizli_kontrol"), icon=":material/ecg_heart:", type="primary", key="hizli_kontrol"):
        saat_simulatoru.olcum_al_ve_kaydet(veritabani.ayar("senaryo"), ortam_kodu)
        st.toast(t("olcum_alindi"), icon=":material/check_circle:")
st.markdown("""<style>
.st-key-hizli_kontrol button {height:58px; width:100%; border-radius:8px; margin-bottom:6px;}
</style>""", unsafe_allow_html=True)


def sonraki_olcum_yazisi(son_zaman: str) -> str:
    sonraki = datetime.strptime(son_zaman, "%Y-%m-%d %H:%M:%S") + timedelta(seconds=aralik)
    bicim = "%H:%M:%S" if aralik < 60 else "%H:%M"
    return f"{t('sonraki_olcum')} {sonraki.strftime(bicim)}" if canli else t("saat_beklemede")


# ---------------------------------------------------------------
# BÖLGE PANELİ (gönderilen örnekteki düzen)
# ---------------------------------------------------------------
def bolge_paneli(secili: str, d: dict, df):
    deg = d["degerlendirme"]
    html(f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">'
         f'<div class="bolum-baslik" style="margin:0">{tx(ayarlar.BOLGELER[secili])}</div>'
         f'{arayuz.rozet(d["bolgeler"][secili])}</div>')

    # --- Radyasyon: saatten değil, görev ortamından hesaplanır ---
    if secili == "radyasyon":
        r = d["radyasyon"]
        html(arayuz.mini_kart({**r, "ad": t("rad_kart")}, r["seri"],
                              f"30 {t('gun')} +{r['son_30_gun']:.0f}"))
        html(f'<div class="bolum-baslik" style="font-size:.95rem">{t("rad_kart_grafik")}</div>')
        baslangic = date.today() - timedelta(days=len(r["seri"]) - 1)
        gunler = [baslangic + timedelta(days=i) for i in range(len(r["seri"]))]
        cizgiler = [(ayarlar.RADYASYON_UYARI, t("uyari_cizgi"), ayarlar.RENKLER["sari"], "dash"),
                    (ayarlar.RADYASYON_KRITIK, t("kritik_cizgi"), ayarlar.RENKLER["kirmizi"], "dot")]
        st.plotly_chart(grafikler.esik_grafigi(gunler, r["seri"], cizgiler, "mSv", x_bicim="%d.%m"),
                        config={"displayModeBar": False}, key="grafik_radyasyon")
        html(arayuz.not_kutusu(f'<b>{r["baslik"]}</b><br>{r["ne_yapmali"]}<br>'
                               f'<span style="color:#94a3b8">{t("rad_not")}</span>', r["renk"]))
        with st.expander(t("ne_demek_soru", ad=r["ad"]), icon=":material/info:"):
            st.write(r["ne_demek"])
            st.write(r["nasil_olculur"])
        return

    metrikler = [m for m in deg.values() if m["bolge"] == secili]

    # --- Özet kartları (sparkline'lı) ---
    kartlar = []
    for m in metrikler:
        seri = df[m["kod"]] if len(df) else []
        fark = (seri.iloc[-1] - seri.iloc[0]) if len(df) > 1 else 0
        kartlar.append(arayuz.mini_kart(m, seri, f"{t('son_n_olcum', n=len(df))} {fark:+.1f}"))
    if secili == "beyin":
        r = d["ruh"]
        gecmis = veritabani.ruh_hali_gecmisi(14)
        deger = f"{d['ruh_kaydi']['ruh_hali']}/5" if d["ruh_kaydi"] else "–"
        kartlar.append(arayuz.mini_kart({"ad": t("ruh_sagligi"), "deger_yazi": deger, "birim": "",
                                         "durum": r["durum"]},
                                        gecmis["ruh_hali"] if len(gecmis) else [], t("son_14_gun")))
    for i in range(0, len(kartlar), 2):
        for sutun, kart in zip(st.columns(2), kartlar[i:i + 2]):
            sutun.markdown(kart, unsafe_allow_html=True)

    # --- Uyarı / Kritik çizgili grafik ---
    if metrikler and len(df) > 1:
        if len(metrikler) > 1:
            kod = st.pills(t("grafik_degeri"), [m["kod"] for m in metrikler],
                           format_func=lambda k: deg[k]["ad"], default=metrikler[0]["kod"],
                           key=f"grafik_{secili}", label_visibility="collapsed") or metrikler[0]["kod"]
        else:
            kod = metrikler[0]["kod"]
        m = deg[kod]
        html(f'<div class="bolum-baslik" style="font-size:.95rem">{m["ad"]}</div>')
        cizgiler = grafikler.esik_cizgileri(kod, t("uyari_cizgi"), t("kritik_cizgi"))
        st.plotly_chart(grafikler.esik_grafigi(df["zaman"], df[kod], cizgiler, m["birim"]),
                        config={"displayModeBar": False}, key=f"esik_{secili}")

    # --- Not kutusu: en önemli adım ---
    adaylar = metrikler + ([{**d["ruh"], "renk": ayarlar.RENKLER[d["ruh"]["durum"]]}] if secili == "beyin" else [])
    if adaylar:
        en_onemli = max(adaylar, key=lambda m: saglik_motoru.DURUM_SIRASI[m["durum"]])
        html(arayuz.not_kutusu(f'<b>{en_onemli["baslik"]}</b><br>'
                               f'<span style="color:#94a3b8">{t("ne_yapmalisin")}:</span> {en_onemli["ne_yapmali"]}',
                               en_onemli["renk"]))
    for m in metrikler:
        with st.expander(t("ne_demek_soru", ad=m["ad"]), icon=":material/info:"):
            st.write(f"**{t('ne_demek')}:** {m['ne_demek']}")
            st.write(f"**{t('nasil_olculur')}:** {m['nasil_olculur']}")
            st.write(f"**{t('normal')}:** {m['normal_yazi']} {m['birim']}")


# ---------------------------------------------------------------
# CANLI PANEL — saatten yeni veri geldikçe kendini yeniler (varsayılan 3 dakika)
# ---------------------------------------------------------------
@st.fragment(run_every=aralik if canli else None)
def canli_panel():
    if canli and saat_simulatoru.olcum_zamani_geldi_mi(aralik - 1):
        saat_simulatoru.olcum_al_ve_kaydet(veritabani.ayar("senaryo"), ortam_kodu)
    d = arayuz.guncel_durum()
    deg = d["degerlendirme"]

    # --- Uyarılar ---
    for u in d["uyarilar"][:3]:
        html(f'<div class="uyari" style="border-left:3px solid {u["renk"]}">{arayuz.nokta(u["durum"])}'
             f'<b>{u["ad"]}: {u["baslik"]}</b><br><span style="color:#94a3b8">{t("ne_yapmalisin")}:</span> '
             f'{u["ne_yapmali"]}</div>')
    if len(d["uyarilar"]) > 3:
        st.caption(t("daha_fazla_uyari", n=len(d["uyarilar"]) - 3))

    # --- Hareketli canlı nabız ---
    components.html(monitor.nabiz_monitoru_html(
        deg["nabiz"]["deger"], deg["spo2"]["deger"], deg["nabiz"]["renk"], "#38bdf8",
        {"baslik": t("canli_nabiz"), "sonraki": sonraki_olcum_yazisi(d["olcum"]["zaman"])}), height=156)

    # --- Anlık değer kartları ---
    arayuz.bolum_basligi(t("anlik_degerler_ust"), t("anlik_degerler_baslik"))
    kodlar = list(ayarlar.METRIKLER)
    for i in range(0, len(kodlar) + 1, 4):
        sutunlar = st.columns(4)
        for sutun, kod in zip(sutunlar, kodlar[i:i + 4]):
            sutun.markdown(arayuz.metrik_karti(deg[kod]), unsafe_allow_html=True)
        if i + 4 > len(kodlar):
            puan = d["puan"]
            renk = ayarlar.RENKLER["yesil" if puan >= 80 else "sari" if puan >= 55 else "kirmizi"]
            sutunlar[len(kodlar) % 4].markdown(
                f'<div class="mkart" style="border-left:2px solid {renk}">'
                f'<div class="mkart-ust"><div class="mikon">{arayuz.ikon("kalkan", renk)}</div>'
                f'<span class="mdurum" style="color:{renk}">{t("son_olcum")} {d["olcum"]["zaman"][11:16]}</span></div>'
                f'<div class="metiket">{t("genel_saglik_puani")}</div>'
                f'<div class="mdeger">{puan}<span class="mbirim">/100</span></div>'
                f'<div class="mnormal">{t("puan_aciklama")}</div></div>', unsafe_allow_html=True)
            break

    # --- Bölge seçimi ---
    st.write("")
    secili = st.pills(t("bolge_sec"), list(ayarlar.BOLGELER), format_func=lambda k: tx(ayarlar.BOLGELER[k]),
                      default="kalp", key="secili_bolge", label_visibility="collapsed") or "kalp"

    sol, sag = st.columns([1, 1.25], gap="large")
    with sol:
        etiketler = tuple(tx(ayarlar.DURUM_YAZILARI[k]) for k in ("yesil", "sari", "kirmizi"))
        components.html(vucut_cizimi.vucut_foto_html(d["bolgeler"], secili, profil.get("cinsiyet"), etiketler,
                                                     isi=deg["isi"]["deger"], termal_baslik=t("termal_baslik"),
                                                     yukseklik=820), height=825)
    with sag:
        with st.container(border=True):
            bolge_paneli(secili, d, veritabani.son_olcumler(60))


canli_panel()

# ---------------------------------------------------------------
# GÖREV ORTAMI (radyasyon, CO2, kabin, yerçekimi, Dünya saati)
# ---------------------------------------------------------------
st.write("")
with st.container(border=True):
    ust, rozet_yeri = st.columns([3, 1])
    with ust:
        arayuz.bolum_basligi(t("ortam_ust"), tx(ortam["ad"]))
    with rozet_yeri:
        html(f'<div style="text-align:right">{arayuz.etiket("yesil")}</div>')
    sol, sag = st.columns([1, 3], vertical_alignment="center")
    with sol:
        html(f'<div class="radyasyon">{arayuz.ikon("radyasyon", "#cbd5e1", 22)}'
             f'<div style="font-size:1.6rem;font-weight:700;color:#f1f5f9">{ortam["radyasyon"]:.2f}</div>'
             f'<div class="kutu-ust">mSv / {t("gun")}</div></div>')
    with sag:
        co2 = ortam["co2"] + random.uniform(-0.02, 0.02)
        kabin = ortam["kabin"] + random.uniform(-0.2, 0.2)
        components.html(arayuz.ortam_kutulari_html([
            ("CO2", f"{co2:.2f}%"),
            (t("kabin"), f"{kabin:.1f}°C"),
            (t("yercekimi"), f"{ortam['yercekimi']:.2f}g"),
        ], t("dunya_saati")), height=96)
        st.caption(tx(ortam["not"]))
