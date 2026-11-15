"""
SAĞLIK MOTORU — Ölçümleri yorumlar.

Her değer için: durum (yeşil/sarı/kırmızı) + ne demek + ne yapmalısın
Her vücut bölgesi için: o bölgedeki en kötü durum
Bu dosya teşhis koymaz; astronotu doğru adıma ve gerekirse doktora yönlendirir.
"""
import ayarlar
from ceviri import t, tx

DURUM_SIRASI = {"yesil": 0, "sari": 1, "kirmizi": 2}


def durum_bul(kod: str, deger: float) -> str:
    m = ayarlar.METRIKLER[kod]
    if m["yesil"][0] <= deger <= m["yesil"][1]:
        return "yesil"
    if m["sari"][0] <= deger <= m["sari"][1]:
        return "sari"
    return "kirmizi"


def en_kotu(durumlar) -> str:
    durumlar = list(durumlar)
    return max(durumlar, key=lambda d: DURUM_SIRASI[d]) if durumlar else "yesil"


def sayi(kod: str, deger) -> str:
    """Ekranda gösterim: 36.7 veya 72 gibi."""
    return f"{deger:.1f}" if kod in ("isi", "uyku") else f"{deger:.0f}"


def normal_aralik_yazisi(kod: str) -> str:
    m = ayarlar.METRIKLER[kod]
    if "normal_yazi" in m:
        return tx(m["normal_yazi"])
    return f"{sayi(kod, m['yesil'][0])}–{sayi(kod, m['yesil'][1])}"


def olcumu_degerlendir(olcum: dict) -> dict:
    sonuc = {}
    for kod, m in ayarlar.METRIKLER.items():
        deger = olcum[kod]
        durum = durum_bul(kod, deger)
        baslik, ne_yapmali = m["mesajlar"][durum]
        ne_yapmali = tx(ne_yapmali)
        if durum == "kirmizi":
            ne_yapmali += " " + tx(ayarlar.DOKTORA_HABER_VER)
        sonuc[kod] = {
            "kod": kod, "ad": tx(m["ad"]), "deger": deger, "deger_yazi": sayi(kod, deger),
            "birim": tx(m["birim"]), "bolge": m["bolge"], "ikon": m["ikon"],
            "durum": durum, "renk": ayarlar.RENKLER[durum], "durum_yazisi": tx(ayarlar.DURUM_YAZILARI[durum]),
            "baslik": tx(baslik), "ne_yapmali": ne_yapmali,
            "ne_demek": tx(m["ne_demek"]), "nasil_olculur": tx(m["nasil_olculur"]),
            "normal_yazi": normal_aralik_yazisi(kod),
        }
    return sonuc


def ruh_halini_degerlendir(kayit) -> dict:
    """Günlük ruh hali kontrolünü yorumlar."""
    if kayit is None:
        return {"durum": "sari", "baslik": t("ruh_yok_baslik"), "ne_yapmali": t("ruh_yok_yapilacak"),
                "iyilik": None}
    iyilik = ((kayit["ruh_hali"] - 1) / 4 + (kayit["enerji"] - 1) / 4
              + (10 - kayit["stres"]) / 9 + (5 - kayit["yalnizlik"]) / 4) / 4
    if iyilik >= 0.6:
        return {"durum": "yesil", "baslik": t("ruh_iyi_baslik"), "ne_yapmali": t("ruh_iyi_yapilacak"),
                "iyilik": iyilik}
    if iyilik >= 0.4:
        return {"durum": "sari", "baslik": t("ruh_orta_baslik"), "ne_yapmali": t("ruh_orta_yapilacak"),
                "iyilik": iyilik}
    return {"durum": "kirmizi", "baslik": t("ruh_kotu_baslik"), "ne_yapmali": t("ruh_kotu_yapilacak"),
            "iyilik": iyilik}


def radyasyon_degerlendir(gorev_gunu: int, ortam_kodu: str) -> dict:
    """
    Kümülatif radyasyon dozu (mSv) = görev günü x ortamın günlük dozu.
    Saatten gelmez; görev ortamına göre hesaplanır. Ölçüm kartlarıyla aynı biçimde döner.
    """
    gunluk = ayarlar.ORTAMLAR[ortam_kodu]["radyasyon"]
    gun = max(1, gorev_gunu)
    seri = [round(gunluk * i, 1) for i in range(1, gun + 1)]
    deger = seri[-1]
    if deger < ayarlar.RADYASYON_UYARI:
        durum = "yesil"
    elif deger < ayarlar.RADYASYON_KRITIK:
        durum = "sari"
    else:
        durum = "kirmizi"
    ne_yapmali = t(f"rad_{durum}_yapilacak")
    if durum == "kirmizi":
        ne_yapmali += " " + tx(ayarlar.DOKTORA_HABER_VER)
    return {
        "kod": "radyasyon", "ad": t("rad_ad"), "deger": deger, "deger_yazi": f"{deger:.1f}" if deger < 10 else f"{deger:.0f}", "birim": "mSv",
        "bolge": "radyasyon", "ikon": "radyasyon", "durum": durum, "renk": ayarlar.RENKLER[durum],
        "durum_yazisi": tx(ayarlar.DURUM_YAZILARI[durum]), "baslik": t(f"rad_{durum}_baslik"),
        "ne_yapmali": ne_yapmali, "ne_demek": t("rad_ne_demek"), "nasil_olculur": t("rad_nasil"),
        "normal_yazi": f"< {ayarlar.RADYASYON_UYARI}", "seri": seri, "gunluk": gunluk,
        "son_30_gun": round(gunluk * min(30, gun), 1),
    }


def bolge_durumlari(degerlendirme: dict, ruh: dict, radyasyon: dict = None) -> dict:
    bolgeler = {kod: [] for kod in ayarlar.BOLGELER}
    for d in degerlendirme.values():
        bolgeler[d["bolge"]].append(d["durum"])
    bolgeler["beyin"].append(ruh["durum"])
    if radyasyon:
        bolgeler["radyasyon"].append(radyasyon["durum"])
    return {kod: en_kotu(liste) for kod, liste in bolgeler.items()}


def saglik_puani(degerlendirme: dict, ruh: dict, radyasyon: dict = None) -> int:
    puanlar = {"yesil": 100, "sari": 60, "kirmizi": 20}
    tum = [d["durum"] for d in degerlendirme.values()] + [ruh["durum"]]
    if radyasyon:
        tum.append(radyasyon["durum"])
    return round(sum(puanlar[d] for d in tum) / len(tum))


def uyarilar(degerlendirme: dict, ruh: dict, radyasyon: dict = None) -> list:
    liste = [d for d in degerlendirme.values() if d["durum"] != "yesil"]
    if radyasyon and radyasyon["durum"] != "yesil":
        liste.append(radyasyon)
    if ruh["durum"] != "yesil":
        liste.append({"ad": t("ruh_sagligi"), "durum": ruh["durum"], "baslik": ruh["baslik"],
                      "ne_yapmali": ruh["ne_yapmali"], "renk": ayarlar.RENKLER[ruh["durum"]]})
    return sorted(liste, key=lambda d: -DURUM_SIRASI[d["durum"]])


def kisisel_oneriler(degerlendirme: dict, kayit) -> list:
    """'Daha iyi olmak için ne yapmalıyım?' — son ölçümlere ve ruh haline göre öneriler."""
    oneriler = []
    if kayit is None:
        oneriler.append(t("oneri_anket"))
    else:
        if kayit["stres"] >= 7:
            oneriler.append(t("oneri_stres"))
        if kayit["yalnizlik"] >= 4:
            oneriler.append(t("oneri_yalnizlik"))
        if kayit["enerji"] <= 2:
            oneriler.append(t("oneri_enerji"))
        if kayit["ruh_hali"] <= 2:
            oneriler.append(t("oneri_ruh_dusuk"))
    if degerlendirme["uyku"]["durum"] != "yesil":
        oneriler.append(t("oneri_uyku"))
    if degerlendirme["hrv"]["durum"] != "yesil":
        oneriler.append(t("oneri_hrv"))
    if degerlendirme["egzersiz"]["durum"] != "yesil":
        oneriler.append(t("oneri_egzersiz"))
    if not oneriler:
        oneriler.append(t("oneri_hepsi_iyi"))
    oneriler.append(t("oneri_genel"))
    return oneriler


def bildirimler(degerlendirme: dict, ruh: dict, yapilanlar: set, profil: dict, ayar) -> list:
    """
    Üst menüdeki bildirim listesi. Her bildirime tıklanınca nereye gidileceği de yazılır:
      {"durum": ..., "metin": ..., "hedef": ("gorev", kod) | ("bolge", bolge) | ("sayfa", dosya)}
    """
    liste = []
    for u in uyarilar(degerlendirme, ruh):
        if u["durum"] == "kirmizi":
            hedef = ("bolge", u["bolge"]) if "bolge" in u else ("sayfa", "sayfalar/destek.py")
            liste.append({"durum": "kirmizi", "metin": f"{u['ad']}: {u['baslik']}", "hedef": hedef})
    if profil and profil.get("cinsiyet") == "Kadın" and ayar("bildirim_dongu") != "0":
        import veritabani
        d = dongu_durumu(veritabani.regl_donemleri())
        if d.get("kayit_var") and not d["acik_donem"]:
            if d["gecikme"] > 0:
                liste.append({"durum": "sari", "metin": t("bildirim_dongu_gecikme", n=d["gecikme"]),
                              "hedef": ("sayfa", "sayfalar/destek.py")})
            elif 0 <= d["kalan_gun"] <= 2:
                liste.append({"durum": "bilgi", "metin": t("bildirim_dongu_yaklasiyor", n=d["kalan_gun"]),
                              "hedef": ("sayfa", "sayfalar/destek.py")})
    if ayar("bildirim_su") == "1" and "su" not in yapilanlar:
        liste.append({"durum": "bilgi", "metin": t("bildirim_su"), "hedef": ("gorev", "su")})
    if ayar("bildirim_ilac") == "1" and profil and (profil.get("ilaclar") or "").strip():
        liste.append({"durum": "bilgi", "metin": t("bildirim_ilac", ilac=profil["ilaclar"]),
                      "hedef": ("sayfa", "sayfalar/gorevler.py")})
    if ayar("bildirim_ruh") == "1" and "ruh_hali" not in yapilanlar:
        liste.append({"durum": "sari", "metin": t("bildirim_ruh"), "hedef": ("sayfa", "sayfalar/destek.py")})
    if ayar("bildirim_gorev") == "1":
        for g in ayarlar.GOREVLER:
            if g["kod"] not in yapilanlar and g["kod"] not in ("su", "ruh_hali"):
                liste.append({"durum": "bilgi", "metin": t("bildirim_gorev", gorev=tx(g["ad"])),
                              "hedef": g["hedef"]})
    return liste


# ---------------------------------------------------------------
# REGL DÖNGÜSÜ
# ---------------------------------------------------------------
def dongu_durumu(donemler: list, bugun=None) -> dict:
    """
    Kayıtlı regl dönemlerinden bugünkü durumu hesaplar.
    Döndürür: gun (döngünün kaçıncı günü), evre, dongu_uzunlugu, regl_suresi,
              sonraki (tahmini sonraki regl tarihi), kalan_gun, gecikme, kayit_var
    """
    from datetime import date, timedelta
    bugun = bugun or date.today()
    if not donemler:
        return {"kayit_var": False}

    baslangiclar = [date.fromisoformat(d["baslangic"]) for d in donemler]
    # ortalama döngü uzunluğu: ardışık başlangıçlar arası (son 6 döngü, makul aralıkta olanlar)
    farklar = [(b - a).days for a, b in zip(baslangiclar, baslangiclar[1:])]
    farklar = [f for f in farklar if ayarlar.DONGU_ARALIGI[0] <= f <= ayarlar.DONGU_ARALIGI[1]][-6:]
    dongu = round(sum(farklar) / len(farklar)) if farklar else ayarlar.VARSAYILAN_DONGU
    # ortalama regl süresi: kapanmış dönemlerden
    sureler = [(date.fromisoformat(d["bitis"]) - date.fromisoformat(d["baslangic"])).days + 1
               for d in donemler if d.get("bitis")]
    sureler = [s for s in sureler if 1 <= s <= 10][-6:]
    regl = round(sum(sureler) / len(sureler)) if sureler else ayarlar.VARSAYILAN_REGL

    son = donemler[-1]
    son_baslangic = date.fromisoformat(son["baslangic"])
    gun = (bugun - son_baslangic).days + 1
    acik = not son.get("bitis")
    ovulasyon = dongu - 14  # ovulasyon genellikle sonraki regl'den ~14 gün önce

    if acik or gun <= regl:
        evre = "regl"
    elif gun < ovulasyon - 1:
        evre = "folikuler"
    elif gun <= ovulasyon + 1:
        evre = "ovulasyon"
    else:
        evre = "luteal"

    sonraki = son_baslangic + timedelta(days=dongu)
    kalan = (sonraki - bugun).days
    return {
        "kayit_var": True, "gun": gun, "evre": evre, "dongu_uzunlugu": dongu, "regl_suresi": regl,
        "ovulasyon_gunu": ovulasyon, "sonraki": sonraki, "kalan_gun": kalan,
        "gecikme": max(0, -kalan) if not acik else 0, "acik_donem": acik,
        "son_baslangic": son_baslangic, "dongu_sayisi": len(farklar),
    }
