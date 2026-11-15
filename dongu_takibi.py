"""
REGL DÖNGÜSÜ TAKİBİ — Güvenlik ve Yardım sayfasında, yalnızca profilde cinsiyet "Kadın" ise görünür.

- Döngü halkası: evreler renkli, bugün işaretli
- Bugünkü evre, sonraki regl tahmini, gecikme uyarısı, evreye göre ipucu
- "Regl başladı" / "Regl bitti" kaydı, günlük akış ve belirti kaydı
- Geçmiş dönemler ve uzayda regl hakkında bilgi
Veriler yalnızca bu cihazdaki veritabanında tutulur. Tahminler bilgilendirme amaçlıdır.
"""
import math
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import arayuz
import ayarlar
import saglik_motoru
import veritabani
from arayuz import html
from ceviri import t, tx


def _evre_listesi(d: dict) -> list:
    """Döngünün her günü için evre: ["regl", "regl", ..., "luteal"]"""
    gunler = []
    for g in range(1, d["dongu_uzunlugu"] + 1):
        if g <= d["regl_suresi"]:
            gunler.append("regl")
        elif g < d["ovulasyon_gunu"] - 1:
            gunler.append("folikuler")
        elif g <= d["ovulasyon_gunu"] + 1:
            gunler.append("ovulasyon")
        else:
            gunler.append("luteal")
    return gunler


def dongu_halkasi(d: dict) -> str:
    """Evreleri renkli dilimler olarak gösteren halka; bugün beyaz noktayla işaretli."""
    gunler = _evre_listesi(d)
    n = len(gunler)
    r, cx, cy = 78, 100, 100
    dilimler = ""
    for i, evre in enumerate(gunler):
        a1 = -math.pi / 2 + 2 * math.pi * i / n + 0.025
        a2 = -math.pi / 2 + 2 * math.pi * (i + 1) / n - 0.025
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        renk = ayarlar.DONGU_EVRELERI[evre]["renk"]
        aktif = i + 1 == min(d["gun"], n)
        dilimler += (f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 0 1 {x2:.1f},{y2:.1f}" stroke="{renk}" '
                     f'stroke-width="{18 if aktif else 13}" fill="none" stroke-linecap="butt" '
                     f'opacity="{1 if aktif else 0.55}"/>')
    gun = min(d["gun"], n)
    a = -math.pi / 2 + 2 * math.pi * (gun - 0.5) / n
    isaret = (f'<circle cx="{cx + r * math.cos(a):.1f}" cy="{cy + r * math.sin(a):.1f}" r="8" fill="#ffffff" '
              f'stroke="#070d18" stroke-width="3"/>')
    evre_renk = ayarlar.DONGU_EVRELERI[d["evre"]]["renk"]
    return f"""
<div style="display:flex;justify-content:center">
<svg viewBox="0 0 200 200" width="220" height="220" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{cx}" cy="{cy}" r="{r}" stroke="#1c2a40" stroke-width="13" fill="none"/>
  {dilimler}{isaret}
  <text x="100" y="88" text-anchor="middle" fill="#8aa0b8" font-size="11" letter-spacing="2"
        font-family="sans-serif">{t("dongu_gunu").upper()}</text>
  <text x="100" y="122" text-anchor="middle" fill="#f8fafc" font-size="38" font-weight="800"
        font-family="sans-serif">{d["gun"]}</text>
  <text x="100" y="142" text-anchor="middle" fill="{evre_renk}" font-size="11" font-weight="700"
        font-family="sans-serif">/ {d["dongu_uzunlugu"]}</text>
</svg></div>"""


def _kutu(baslik, deger, alt="", renk="#f1f5f9"):
    return (f'<div class="kutu" style="text-align:left;padding:12px 14px;margin-bottom:10px">'
            f'<div class="kutu-ust">{baslik}</div>'
            f'<div style="font-size:1.15rem;font-weight:800;color:{renk};margin-top:4px">{deger}</div>'
            f'<div class="gri" style="font-size:.78rem;margin-top:2px">{alt}</div></div>')


def goster():
    """Bölümü çizer. Destek sayfası bunu yalnızca kadın profillerde çağırır."""
    bugun = date.today()
    donemler = veritabani.regl_donemleri()
    d = saglik_motoru.dongu_durumu(donemler, bugun)

    with st.container(border=True):
        html(f'<div class="bolum-ust" style="color:#f472b6">{t("dongu_ust")}</div>'
             f'<div class="bolum-baslik">{t("dongu_baslik")}</div>')
        st.caption(t("dongu_gizlilik"))

        # --- Hiç kayıt yoksa: son regl başlangıcını sor ---
        if not d["kayit_var"]:
            st.info(t("dongu_ilk_kayit"), icon=":material/info:")
            c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
            tarih = c1.date_input(t("dongu_son_baslangic"), value=bugun, max_value=bugun, format="DD.MM.YYYY",
                                  key="dongu_ilk_tarih")
            if c2.button(t("kaydet"), icon=":material/save:", type="primary", key="dongu_ilk_kaydet"):
                veritabani.regl_baslat(tarih.isoformat())
                if (bugun - tarih).days >= ayarlar.VARSAYILAN_REGL:
                    veritabani.regl_bitir((tarih + timedelta(days=ayarlar.VARSAYILAN_REGL - 1)).isoformat())
                st.rerun()
            return

        evre = ayarlar.DONGU_EVRELERI[d["evre"]]
        sol, sag = st.columns([1, 1.4], gap="large", vertical_alignment="center")
        with sol:
            html(dongu_halkasi(d))
            html('<div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;font-size:.72rem;'
                 'color:#8aa0b8">' + "".join(
                     f'<span>{arayuz.nokta(v["renk"])}{tx(v["ad"])}</span>' for v in ayarlar.DONGU_EVRELERI.values())
                 + '</div>')
        with sag:
            if d["acik_donem"]:
                sonraki_yazi, sonraki_alt = t("dongu_regl_devam"), t("dongu_regl_gunu", n=d["gun"])
            elif d["gecikme"] > 0:
                sonraki_yazi = d["sonraki"].strftime("%d.%m.%Y")
                sonraki_alt = t("dongu_gecikti", n=d["gecikme"])
            else:
                sonraki_yazi = d["sonraki"].strftime("%d.%m.%Y")
                sonraki_alt = t("bugun") if d["kalan_gun"] == 0 else t("dongu_kalan", n=d["kalan_gun"])
            k1, k2 = st.columns(2)
            k1.markdown(_kutu(t("dongu_evre"), tx(evre["ad"]), t("dongu_gun_bilgi", n=d["gun"]), evre["renk"]),
                        unsafe_allow_html=True)
            k2.markdown(_kutu(t("dongu_sonraki"), sonraki_yazi, sonraki_alt,
                              ayarlar.RENKLER["sari"] if d["gecikme"] else "#f1f5f9"), unsafe_allow_html=True)
            k3, k4 = st.columns(2)
            k3.markdown(_kutu(t("dongu_ortalama"), f'{d["dongu_uzunlugu"]} {t("gun")}',
                              t("dongu_hesap", n=d["dongu_sayisi"]) if d["dongu_sayisi"] else t("dongu_varsayilan")),
                        unsafe_allow_html=True)
            k4.markdown(_kutu(t("dongu_regl_suresi"), f'{d["regl_suresi"]} {t("gun")}', t("dongu_ortalama_alt")),
                        unsafe_allow_html=True)
            if d["gecikme"] > 0:
                html(arayuz.not_kutusu(t("dongu_gecikme_notu", n=d["gecikme"]), ayarlar.RENKLER["sari"]))
            else:
                html(arayuz.not_kutusu(f'<b>{tx(evre["ad"])}</b><br>{tx(evre["ipucu"])}', evre["renk"]))

        # --- Regl başladı / bitti ---
        st.write("")
        c1, c2, c3 = st.columns([1.3, 1, 1], vertical_alignment="bottom")
        tarih = c1.date_input(t("tarih"), value=bugun, max_value=bugun, format="DD.MM.YYYY", key="dongu_tarih")
        if d["acik_donem"]:
            if c2.button(t("dongu_bitti"), icon=":material/check_circle:", type="primary", key="dongu_bitir"):
                veritabani.regl_bitir(max(tarih, d["son_baslangic"]).isoformat())
                st.session_state["bildirim"] = t("kaydedildi")
                st.rerun()
        else:
            if c2.button(t("dongu_basladi"), icon=":material/water_drop:", type="primary", key="dongu_baslat"):
                veritabani.regl_baslat(tarih.isoformat())
                st.session_state["bildirim"] = t("kaydedildi")
                st.rerun()

        # --- Bugünkü belirtiler ---
        with st.expander(t("dongu_belirti_baslik"), icon=":material/edit_note:",
                         expanded=d["evre"] == "regl"):
            kayit = veritabani.regl_belirtisi(bugun.isoformat()) or {}
            akis = st.segmented_control(t("dongu_akis"), list(ayarlar.REGL_AKIS),
                                        format_func=lambda k: tx(ayarlar.REGL_AKIS[k]),
                                        default=kayit.get("akis") or ("orta" if d["evre"] == "regl" else "yok"),
                                        key="dongu_akis")
            belirtiler = st.pills(t("dongu_belirtiler"), list(ayarlar.REGL_BELIRTILERI), selection_mode="multi",
                                  format_func=lambda k: tx(ayarlar.REGL_BELIRTILERI[k]),
                                  default=kayit.get("belirtiler") or [], key="dongu_belirtiler")
            notu = st.text_input(t("soru_not"), value=kayit.get("notu") or "", key="dongu_not")
            if st.button(t("kaydet"), icon=":material/save:", key="dongu_belirti_kaydet"):
                veritabani.regl_belirti_kaydet(bugun.isoformat(), akis or "yok", list(belirtiler or []), notu)
                st.session_state["bildirim"] = t("kaydedildi")
                st.rerun()

        # --- Geçmiş dönemler ---
        with st.expander(t("dongu_gecmis"), icon=":material/history:"):
            satirlar = []
            for onceki, simdiki in zip([None] + donemler[:-1], donemler):
                bas = date.fromisoformat(simdiki["baslangic"])
                bit = date.fromisoformat(simdiki["bitis"]) if simdiki.get("bitis") else None
                dongu = (bas - date.fromisoformat(onceki["baslangic"])).days if onceki else None
                satirlar.append({
                    t("dongu_tablo_baslangic"): bas.strftime("%d.%m.%Y"),
                    t("dongu_tablo_bitis"): bit.strftime("%d.%m.%Y") if bit else t("dongu_regl_devam"),
                    t("dongu_regl_suresi"): f"{(bit - bas).days + 1} {t('gun')}" if bit else "-",
                    t("dongu_tablo_dongu"): f"{dongu} {t('gun')}" if dongu else "-",
                })
            st.dataframe(pd.DataFrame(satirlar[::-1]), hide_index=True)
            if st.button(t("dongu_son_sil"), icon=":material/delete:", key="dongu_sil", type="tertiary"):
                veritabani.regl_donem_sil(donemler[-1]["id"])
                st.rerun()

        with st.expander(t("dongu_uzay_baslik"), icon=":material/rocket_launch:"):
            st.markdown(t("dongu_uzay_metin"))
