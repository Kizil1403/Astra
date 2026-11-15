"""
ÇEVİRİ — Uygulamadaki tüm yazılar birçok dilde.

- Türkçe, İngilizce, İspanyolca, Rusça: elle çevrildi (sozluk.py ve ayarlar.py içinde).
- Diğer önemli diller (Fransızca, Almanca, Arapça, Çince...): deep-translator ile otomatik çevrilir.
  Bir dil ilk kez seçildiğinde bütün yazılar tek seferde çevrilir ve veritabanına kaydedilir;
  sonraki açılışlarda internet gerekmez.

Kullanım:  t("anahtar")              -> seçili dildeki yazı
           tx({"tr": ..., "en": ...}) -> çok dilli bir sözlükten seçili dildeki yazı
"""
import functools
import re
import sqlite3

import streamlit as st

from sozluk import SOZLUK

# Seçilebilir diller: kod -> (kendi dilindeki adı, Türkçe adı)
DILLER = {
    "tr": ("Türkçe", "Türkçe"),
    "en": ("English", "İngilizce"),
    "es": ("Español", "İspanyolca"),
    "ru": ("Русский", "Rusça"),
    "fr": ("Français", "Fransızca"),
    "de": ("Deutsch", "Almanca"),
    "it": ("Italiano", "İtalyanca"),
    "pt": ("Português", "Portekizce"),
    "ar": ("العربية", "Arapça"),
    "zh-CN": ("中文", "Çince"),
    "ja": ("日本語", "Japonca"),
    "ko": ("한국어", "Korece"),
    "hi": ("हिन्दी", "Hintçe"),
    "az": ("Azərbaycan", "Azerbaycanca"),
}
DIL_ADLARI = {kod: ad for kod, (ad, _) in DILLER.items()}
ELLE_CEVRILEN = {"tr", "en", "es", "ru"}

EKSIK_ANAHTARLAR = set()  # test için: çevirisi olmayan anahtarlar
_ONBELLEK = {}            # {dil: {ingilizce_yazı: çeviri}}


def aktif_dil() -> str:
    try:
        return st.session_state.get("dil", "tr")
    except Exception:
        return "tr"


# ---------------------------------------------------------------
# Otomatik çeviri önbelleği (veritabanında)
# ---------------------------------------------------------------
def _db():
    import veritabani
    b = sqlite3.connect(veritabani.VERITABANI_DOSYASI)
    b.execute("CREATE TABLE IF NOT EXISTS ceviri_onbellek (dil TEXT, kaynak TEXT, ceviri TEXT, "
              "PRIMARY KEY (dil, kaynak))")
    return b


def _onbellek(dil: str) -> dict:
    if dil not in _ONBELLEK:
        with _db() as b:
            _ONBELLEK[dil] = dict(b.execute("SELECT kaynak, ceviri FROM ceviri_onbellek WHERE dil = ?",
                                            (dil,)).fetchall())
    return _ONBELLEK[dil]


def _kaydet(dil: str, ceviriler: dict):
    _onbellek(dil).update(ceviriler)
    with _db() as b:
        b.executemany("INSERT OR REPLACE INTO ceviri_onbellek (dil, kaynak, ceviri) VALUES (?, ?, ?)",
                      [(dil, k, v) for k, v in ceviriler.items()])


def _makine(metin: str, dil: str) -> str:
    """Önbellekte varsa çeviriyi, yoksa İngilizcesini döndürür (çeviri hazirla() ile önceden yapılır)."""
    if not metin or dil in ELLE_CEVRILEN:
        return metin
    return _onbellek(dil).get(metin, metin)


# ---------------------------------------------------------------
# Ana fonksiyonlar
# ---------------------------------------------------------------
def tx(metin):
    """Çok dilli sözlükse seçili dildeki yazıyı, düz yazıysa kendisini döndürür."""
    if isinstance(metin, dict):
        dil = aktif_dil()
        if dil in metin:
            return metin[dil]
        ingilizce = metin.get("en") or metin.get("tr")
        if dil in ELLE_CEVRILEN:
            return ingilizce
        if isinstance(ingilizce, list):
            return [_makine(s, dil) for s in ingilizce]
        return _makine(ingilizce, dil)
    return metin


def t(anahtar: str, **degiskenler) -> str:
    giris = SOZLUK.get(anahtar)
    if giris is None:
        EKSIK_ANAHTARLAR.add(anahtar)
        return anahtar
    yazi = tx(giris)
    try:
        return yazi.format(**degiskenler) if degiskenler else yazi
    except (KeyError, IndexError, ValueError):  # makine çevirisi yer tutucuyu bozduysa İngilizcesi
        return SOZLUK[anahtar]["en"].format(**degiskenler)


# ---------------------------------------------------------------
# Bir dili hazırlamak: bütün yazıları toplu çevirip kaydeder
# ---------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def _tum_ingilizce_yazilar() -> tuple:
    import ayarlar
    yazilar = []

    def topla(nesne):
        if isinstance(nesne, dict):
            if "en" in nesne and "tr" in nesne:
                en = nesne["en"]
                yazilar.extend(en if isinstance(en, list) else [en])
            else:
                for v in nesne.values():
                    topla(v)
        elif isinstance(nesne, (list, tuple)):
            for v in nesne:
                topla(v)

    topla(SOZLUK)
    for ad in dir(ayarlar):
        if ad.isupper():
            topla(getattr(ayarlar, ad))
    return tuple(dict.fromkeys(y for y in yazilar if isinstance(y, str) and y.strip()))


_YER_TUTUCU = re.compile(r"\{[a-z_]+\}")


def _koru(metin):
    """{n} gibi yer tutucuları çeviri sırasında bozulmasın diye geçici işaretlere çevirir."""
    tutucular = _YER_TUTUCU.findall(metin)
    for i, tutucu in enumerate(tutucular):
        metin = metin.replace(tutucu, f"[{i}]", 1)
    return metin, tutucular


def _geri_al(metin, tutucular):
    for i, tutucu in enumerate(tutucular):
        if f"[{i}]" not in metin:
            return None
        metin = metin.replace(f"[{i}]", tutucu, 1)
    return metin


def hazir_mi(dil: str) -> bool:
    if dil in ELLE_CEVRILEN:
        return True
    eksik = [y for y in _tum_ingilizce_yazilar() if y not in _onbellek(dil)]
    return len(eksik) == 0


def hazirla(dil: str, ilerleme=None) -> int:
    """Seçilen dil için eksik yazıları deep-translator ile çevirir. Çevrilen yazı sayısını döndürür."""
    from deep_translator import GoogleTranslator

    cevirmen = GoogleTranslator(source="en", target=dil)
    eksikler = [y for y in _tum_ingilizce_yazilar() if y not in _onbellek(dil)]
    # tek satırlıları birleştirerek az sayıda istekle çevir (her istek en fazla ~4500 karakter)
    parcalar, parca, uzunluk = [], [], 0
    for y in eksikler:
        if "\n" in y:
            parcalar.append([y])
            continue
        if uzunluk + len(y) > 4000 and parca:
            parcalar.append(parca)
            parca, uzunluk = [], 0
        parca.append(y)
        uzunluk += len(y) + 1
    if parca:
        parcalar.append(parca)

    toplam = 0
    for i, parca in enumerate(parcalar):
        korunan = [_koru(y) for y in parca]
        sonuc = {}
        try:
            cevrilen = cevirmen.translate("\n".join(k[0] for k in korunan)) or ""
            satirlar = cevrilen.split("\n") if len(parca) > 1 else [cevrilen]
        except Exception:
            satirlar = []
        if len(satirlar) != len(parca):  # satır sayısı tutmadıysa tek tek çevir
            satirlar = []
            for k in korunan:
                try:
                    satirlar.append(cevirmen.translate(k[0]) or k[0])
                except Exception:
                    satirlar.append(None)
        for asil, (_, tutucular), ceviri in zip(parca, korunan, satirlar):
            if ceviri:
                geri = _geri_al(ceviri.strip(), tutucular)
                sonuc[asil] = geri if geri else asil
        _kaydet(dil, sonuc)
        toplam += len(sonuc)
        if ilerleme:
            ilerleme((i + 1) / len(parcalar))
    if eksikler and toplam == 0:
        raise ConnectionError("çeviri servisine ulaşılamadı")
    return toplam
