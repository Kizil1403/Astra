"""
POLARIS — ASTRA'nın yapay zeka asistanı

İki modda çalışır:
1) ÇEVRİMİÇİ: Ayarlar sayfasına Gemini API anahtarı girilirse Google Gemini modeli cevap verir.
   Modele astronotun profili, son ölçümleri ve ruh hali "bağlam" olarak verilir.
2) ÇEVRİMDIŞI: Anahtar yoksa (veya internet yoksa) basit kurallarla, son ölçümlere göre cevap verir.

Gemini'ye nasıl cevap vereceği söylenmez; yalnızca adı (Polaris) ve ASTRA'daki tüm güncel değerler
bağlam olarak verilir. Mesajla birlikte ses, video, belge ve görsel gönderilebilir.
"""
import ayarlar
from ceviri import t, tx, DIL_ADLARI, aktif_dil

KRIZ_KELIMELERI = [
    "intihar", "kendime zarar", "ölmek istiyorum", "yaşamak istemiyorum", "canıma kıy",
    "suicide", "kill myself", "self-harm", "self harm", "hurt myself", "want to die",
    "suicidio", "quiero morir", "hacerme daño", "суицид", "покончить с собой", "хочу умереть",
]


def kriz_var_mi(metin: str) -> bool:
    kucuk = metin.lower()
    return any(k in kucuk for k in KRIZ_KELIMELERI)


def sistem_talimati(profil: dict, degerlendirme: dict, ruh: dict, ortam_kodu: str, radyasyon: dict = None,
                    gorev_modu: bool = False) -> str:
    """
    Gemini'ye verilen bağlam: yalnızca Polaris'in kim olduğu ve ASTRA'daki TÜM güncel değerler.
    Nasıl cevap vereceğine dair kural yazılmaz; Gemini kendi bildiği gibi cevap verir.
    """
    ortam = ayarlar.ORTAMLAR[ortam_kodu]
    satirlar = [f"- {d['ad']}: {d['deger_yazi']} {d['birim']} (normal: {d['normal_yazi']}, {d['durum_yazisi']})"
                for d in degerlendirme.values()]
    if radyasyon:
        satirlar.append(f"- {radyasyon['ad']}: {radyasyon['deger_yazi']} mSv "
                        f"({radyasyon['gunluk']} mSv/{t('gun')}, {radyasyon['durum_yazisi']})")
    if profil.get("cinsiyet") == "Kadın":
        import veritabani
        from saglik_motoru import dongu_durumu
        dongu = dongu_durumu(veritabani.regl_donemleri())
        if dongu.get("kayit_var"):
            satirlar.append(f"- {t('dongu_baslik')}: {t('dongu_gun_bilgi', n=dongu['gun'])}, "
                            f"{tx(ayarlar.DONGU_EVRELERI[dongu['evre']]['ad'])}, "
                            f"{t('dongu_sonraki')}: {dongu['sonraki'].isoformat()}"
                            + (f", {t('dongu_gecikti', n=dongu['gecikme'])}" if dongu["gecikme"] else ""))
    satirlar += [
        f"- {t('ruh_sagligi')}: {ruh['baslik']}",
        f"- {t('ortam')}: {tx(ortam['ad'])} | {t('yercekimi')}: {ortam['yercekimi']} g | "
        f"CO2: {ortam['co2']}% | {t('kabin')}: {ortam['kabin']} °C | {ortam['radyasyon']} mSv/{t('gun')}",
    ]
    yas = ""
    if profil.get("dogum_yili"):
        from datetime import date
        yas = str(date.today().year - int(profil["dogum_yili"]))
    baglam = f"""Senin adın Polaris. ASTRA mürettebat sağlık ve destek sisteminin yapay zekasısın.

ASTRONOT: {profil.get('ad', '')} {profil.get('soyad', '')} | {profil.get('unvan', '')} | {profil.get('cinsiyet', '')} | \
{yas} | {profil.get('boy', '')} cm | {profil.get('kilo', '')} kg | {profil.get('kan_grubu', '')} | \
{t('kronik_hastalik')} {profil.get('kronik_hastalik') or '-'} | {t('ilaclar')}: {profil.get('ilaclar') or '-'} | \
{t('alerjiler')}: {profil.get('alerjiler') or '-'}

ASTRA GÜNCEL DEĞERLER:
{chr(10).join(satirlar)}
"""
    if gorev_modu:
        baglam += "\nMOD: Görev — kullanıcı bu isteği bir görev olarak yapmak istiyor.\n"
    return baglam


# Güncel Gemini modelleri (Kasım 2026). Google yeni projeler için 3.8 Flash ve 3.5 Flash-Lite öneriyor.
VARSAYILAN_MODEL = "gemini-3.5-flash-lite"
MODEL_SECENEKLERI = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-4-argon",
                     "gemini-flash-latest", "gemini-2.5-flash"]
# Seçilen model çalışmazsa sırayla denenecek modeller
YEDEK_MODELLER = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.6-flash",
                  "gemini-2.5-flash"]
# Kapatılmış veya eski modeller kayıtlıysa otomatik olarak güncel modele geçilir
ESKI_MODELLER = ("gemini-1.", "gemini-2.0", "gemini-pro")


def etkin_model(kayitli: str) -> str:
    if not kayitli or kayitli.startswith(ESKI_MODELLER):
        return VARSAYILAN_MODEL
    return kayitli


def _istemci(anahtar):
    from google import genai
    return genai.Client(api_key=anahtar)


def _yanit_metni(yanit) -> str:
    """Gemini cevabından metni güvenli şekilde çıkarır (bazen .text boş gelir)."""
    try:
        if yanit.text:
            return yanit.text
    except Exception:
        pass
    parcalar = []
    for aday in (getattr(yanit, "candidates", None) or []):
        icerik = getattr(aday, "content", None)
        for p in (getattr(icerik, "parts", None) or []):
            if getattr(p, "text", None):
                parcalar.append(p.text)
    return "".join(parcalar)


def kullanilabilir_modeller(anahtar) -> list:
    """API anahtarının erişebildiği metin modelleri (yeniden eskiye)."""
    modeller = []
    for m in _istemci(anahtar).models.list():
        ad = getattr(m, "name", "").replace("models/", "")
        eylemler = getattr(m, "supported_actions", None) or []
        if (ad.startswith("gemini") and (not eylemler or "generateContent" in eylemler)
                and not any(k in ad for k in ("tts", "image", "audio", "live", "embedding", "transcribe"))):
            modeller.append(ad)
    return sorted(modeller, reverse=True)


def _gecici_hata_mi(hata) -> bool:
    """Model bulunamadı, kota doldu ya da sunucu meşgul: başka model denenebilir."""
    metin = str(hata).lower()
    return any(k in metin for k in ("404", "not found", "429", "resource_exhausted", "quota", "503",
                                    "unavailable", "overloaded", "500", "internal", "deadline"))


def gemini_cevap(anahtar, model, sistem, gecmis, soru, ekler=None):
    """
    (cevap, kullanılan_model) döndürür. Model çalışmazsa önce yedekleri, sonra anahtarın modellerini dener.
    ekler: [(veri_bytes, mime_tipi), ...] — ses, video, belge, görsel
    """
    from google.genai import types

    istemci = _istemci(anahtar)
    icerik = [types.Content(role="user" if m["rol"] == "user" else "model", parts=[types.Part(text=m["metin"])])
              for m in gecmis if m.get("metin")]
    parcalar = [types.Part.from_bytes(data=veri, mime_type=tip) for veri, tip in (ekler or [])]
    parcalar.append(types.Part(text=soru or "."))
    icerik.append(types.Content(role="user", parts=parcalar))
    ayar = types.GenerateContentConfig(system_instruction=sistem)

    def dene(m):
        yanit = istemci.models.generate_content(model=m, contents=icerik, config=ayar)
        metin = _yanit_metni(yanit)
        if not metin.strip():
            raise RuntimeError("503 empty response")
        return metin

    denenecek = [etkin_model(model)] + [m for m in YEDEK_MODELLER if m != etkin_model(model)]
    son_hata = None
    for m in denenecek:
        try:
            return dene(m), m
        except Exception as hata:
            son_hata = hata
            if not _gecici_hata_mi(hata):  # API anahtarı hatalı vb.: diğer modeller de çalışmaz
                raise
    # Hiçbiri olmadıysa: anahtarın erişebildiği modellerden ilk çalışanı kullan
    try:
        for m in kullanilabilir_modeller(anahtar)[:5]:
            if m in denenecek:
                continue
            try:
                return dene(m), m
            except Exception as hata:
                son_hata = hata
    except Exception:
        pass
    raise son_hata


def baglanti_testi(anahtar, model):
    """Ayarlar sayfasındaki 'Bağlantıyı test et' düğmesi için. (başarılı_mı, mesaj, kullanılabilir_modeller)"""
    try:
        metin, kullanilan = gemini_cevap(anahtar, model, "Reply with one short sentence.", [], "Say hello.")
        return True, f"{kullanilan}: {metin.strip()[:120]}", []
    except ImportError:
        return False, "google-genai paketi yüklü değil. Terminalde: pip install google-genai", []
    except Exception as hata:
        try:
            modeller = kullanilabilir_modeller(anahtar)
        except Exception:
            modeller = []
        return False, str(hata)[:400], modeller[:15]


def cevrimdisi_cevap(soru: str, degerlendirme: dict, ruh: dict) -> str:
    """İnternet / API anahtarı yokken kurallara dayalı cevap."""
    s = soru.lower()

    def blok(kod):
        d = degerlendirme[kod]
        return (f"**{d['ad']}: {d['deger_yazi']} {d['birim']}** ({d['durum_yazisi']}, normal: {d['normal_yazi']})"
                f"\n\n{d['baslik']}. {d['ne_yapmali']}\n\n{d['ne_demek']}")

    konular = [
        (["nabız", "nabiz", "kalp", "heart", "pulse", "corazón", "pulso", "пульс", "сердце"], ["nabiz"]),
        (["oksijen", "oxygen", "spo2", "nefes", "breath", "oxígeno", "кислород", "дыхан"], ["spo2", "solunum"]),
        (["uyku", "uyuy", "sleep", "sueño", "dormir", "сон", "спать"], ["uyku"]),
        (["ateş", "ısı", "sıcaklık", "fever", "temperature", "fiebre", "температур"], ["isi"]),
        (["egzersiz", "spor", "kas", "kemik", "exercise", "muscle", "bone", "ejercicio", "упражн"], ["egzersiz"]),
        (["stres", "stress", "kaygı", "endişe", "anxiety", "estrés", "ansiedad", "тревог"], ["hrv"]),
    ]
    parcalar = []
    for kelimeler, kodlar in konular:
        if any(k in s for k in kelimeler):
            parcalar += [blok(k) for k in kodlar]

    if kriz_var_mi(soru):
        return t("ai_kriz")
    if any(k in s for k in ["yalnız", "özle", "aile", "dünya", "ev ", "lonely", "homesick", "miss", "family",
                            "earth", "solo", "soledad", "extraño", "familia", "одинок", "скучаю", "семь"]):
        parcalar.append(t("ai_yalnizlik"))
    if any(k in s for k in ["stres", "stress", "kaygı", "anxiety", "estrés", "тревог"]):
        parcalar.append(t("ai_stres"))

    if any(k in s for k in ["değer", "durum", "nasıl", "yorumla", "value", "status", "how am i", "valores",
                            "estado", "показател", "состояни"]) and not parcalar:
        sorunlu = [d for d in degerlendirme.values() if d["durum"] != "yesil"]
        if not sorunlu:
            parcalar.append(t("ai_hepsi_normal"))
        for d in sorunlu:
            parcalar.append(f"**{d['ad']}** ({d['durum_yazisi']}): {d['baslik']}. {d['ne_yapmali']}")
        parcalar.append(f"**{t('ruh_sagligi')}:** {ruh['baslik']}. {ruh['ne_yapmali']}")

    if not parcalar:
        return t("ai_varsayilan")
    return "\n\n".join(parcalar) + "\n\n---\n" + t("ai_cevrimdisi_not")


def cevap_ver(soru, gecmis, profil, degerlendirme, ruh, ortam_kodu, anahtar, model, radyasyon=None,
              ekler=None, gorev_modu=False):
    """Polaris'in cevabı. (cevap, kullanılan_mod) döndürür."""
    if anahtar:
        try:
            sistem = sistem_talimati(profil, degerlendirme, ruh, ortam_kodu, radyasyon, gorev_modu)
            metin, _ = gemini_cevap(anahtar, model, sistem, gecmis, soru, ekler)
            return metin, "gemini"
        except ImportError:
            hata_metni = t("ai_paket_yok")
        except Exception as hata:
            hata_metni = t("ai_baglanti_hatasi", hata=str(hata)[:200])
        return cevrimdisi_cevap(soru, degerlendirme, ruh) + "\n\n" + hata_metni, "cevrimdisi"
    return cevrimdisi_cevap(soru, degerlendirme, ruh), "cevrimdisi"
