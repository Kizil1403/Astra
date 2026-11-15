"""
VERİTABANI — Uygulamanın hafızası (SQLite, tek dosya: astronot_saglik.db)

Tablolar:
  profil               -> kayıt anketindeki bilgiler (ad, unvan, sağlık geçmişi...)
  ayarlar              -> uygulama ayarları (dil, canlı veri, API anahtarı...)
  olcumler             -> saatten gelen ölçümler
  ruh_hali             -> günlük ruh hali kontrolleri
  tamamlanan_gorevler  -> yapılan görevler ve puanlar
  gunluk               -> günlük kayıtları (yazı / ses / video)
  destek_talepleri     -> doktor / psikolog destek istekleri
  sohbet               -> yapay zeka asistanı ile konuşmalar
"""
import os
import sqlite3
from datetime import datetime, date, timedelta

import pandas as pd

VERITABANI_DOSYASI = "astronot_saglik.db"
KAYIT_KLASORU = "kayitlar"  # ses ve video dosyaları buraya kaydedilir


def baglan():
    return sqlite3.connect(VERITABANI_DOSYASI)


def simdi():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def bugun():
    return date.today().isoformat()


def _satir(sorgu, parametreler=()):
    with baglan() as b:
        b.row_factory = sqlite3.Row
        s = b.execute(sorgu, parametreler).fetchone()
    return dict(s) if s else None


def _tablo(sorgu, parametreler=()):
    with baglan() as b:
        return pd.read_sql_query(sorgu, b, params=parametreler)


# ---------------------------------------------------------------
# KURULUM
# ---------------------------------------------------------------
def kur():
    with baglan() as b:
        b.executescript("""
            CREATE TABLE IF NOT EXISTS profil (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                ad TEXT, soyad TEXT, unvan TEXT, cinsiyet TEXT,
                dogum_yili INTEGER, boy INTEGER, kilo REAL, kan_grubu TEXT,
                kronik_hastalik TEXT, ilaclar TEXT, alerjiler TEXT,
                gorev_baslangic TEXT, kayit_zamani TEXT
            );
            CREATE TABLE IF NOT EXISTS ayarlar (
                anahtar TEXT PRIMARY KEY, deger TEXT
            );
            CREATE TABLE IF NOT EXISTS olcumler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zaman TEXT, ortam TEXT,
                nabiz REAL, spo2 REAL, solunum REAL, isi REAL, hrv REAL, uyku REAL, egzersiz REAL
            );
            CREATE TABLE IF NOT EXISTS ruh_hali (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zaman TEXT, ruh_hali INTEGER, stres INTEGER, enerji INTEGER, yalnizlik INTEGER, notu TEXT
            );
            CREATE TABLE IF NOT EXISTS tamamlanan_gorevler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT, gorev_kodu TEXT, puan INTEGER,
                UNIQUE(tarih, gorev_kodu)
            );
            CREATE TABLE IF NOT EXISTS gunluk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zaman TEXT, baslik TEXT, tur TEXT, metin TEXT, ruh_hali INTEGER, dosya_yolu TEXT
            );
            CREATE TABLE IF NOT EXISTS destek_talepleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zaman TEXT, tur TEXT, notu TEXT
            );
            CREATE TABLE IF NOT EXISTS regl_donemleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                baslangic TEXT, bitis TEXT
            );
            CREATE TABLE IF NOT EXISTS regl_belirtileri (
                tarih TEXT PRIMARY KEY, akis TEXT, belirtiler TEXT, notu TEXT
            );
            CREATE TABLE IF NOT EXISTS sohbet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zaman TEXT, rol TEXT, metin TEXT
            );
        """)


# ---------------------------------------------------------------
# PROFİL
# ---------------------------------------------------------------
PROFIL_ALANLARI = ["ad", "soyad", "unvan", "cinsiyet", "dogum_yili", "boy", "kilo", "kan_grubu",
                   "kronik_hastalik", "ilaclar", "alerjiler", "gorev_baslangic"]


def profil_getir():
    return _satir("SELECT * FROM profil WHERE id = 1")


def profil_kaydet(bilgi: dict):
    degerler = [bilgi.get(a) for a in PROFIL_ALANLARI]
    with baglan() as b:
        b.execute(
            f"INSERT OR REPLACE INTO profil (id, {', '.join(PROFIL_ALANLARI)}, kayit_zamani) "
            f"VALUES (1, {', '.join('?' * len(PROFIL_ALANLARI))}, ?)",
            (*degerler, simdi()),
        )


# ---------------------------------------------------------------
# AYARLAR (anahtar - değer)
# ---------------------------------------------------------------
VARSAYILAN_AYARLAR = {
    "dil": "tr",
    "ortam": "iss",
    "senaryo": "normal",
    "canli": "1",
    "olcum_araligi": "180",  # saniye (3 dakika)
    "bildirim_su": "1",
    "bildirim_gorev": "1",
    "bildirim_ruh": "1",
    "bildirim_ilac": "1",
    "bildirim_dongu": "1",
    "gemini_anahtar": "",
    "gemini_model": "gemini-3.5-flash-lite",
}


def gizli_ayar(ad: str, varsayilan=None):
    """Streamlit'in gizli ayarlarından (secrets) bir değer okur. secrets yoksa varsayılanı döndürür.
    İnternetteki sürümde Gemini anahtarı ve bulut modu buradan gelir."""
    try:
        import streamlit as st
        return st.secrets.get(ad, varsayilan)
    except Exception:
        return varsayilan


def gemini_anahtari() -> str:
    """Önce sunucunun gizli ayarı (GEMINI_API_KEY), yoksa kullanıcının Ayarlar'a girdiği anahtar."""
    return (gizli_ayar("GEMINI_API_KEY") or "").strip() or ayar("gemini_anahtar")


def kullanici_klasorunu_ayarla(kimlik: str):
    """Bulut modunda her kullanıcıya ayrı veritabanı ve kayıt klasörü."""
    global VERITABANI_DOSYASI, KAYIT_KLASORU
    os.makedirs("kullanicilar", exist_ok=True)
    VERITABANI_DOSYASI = os.path.join("kullanicilar", f"{kimlik}.db")
    KAYIT_KLASORU = os.path.join("kullanicilar", f"{kimlik}_kayitlar")


def ayar(anahtar: str) -> str:
    s = _satir("SELECT deger FROM ayarlar WHERE anahtar = ?", (anahtar,))
    return s["deger"] if s else VARSAYILAN_AYARLAR.get(anahtar, "")


def ayar_kaydet(anahtar: str, deger):
    with baglan() as b:
        b.execute("INSERT OR REPLACE INTO ayarlar (anahtar, deger) VALUES (?, ?)", (anahtar, str(deger)))


# ---------------------------------------------------------------
# ÖLÇÜMLER
# ---------------------------------------------------------------
OLCUM_SUTUNLARI = ["nabiz", "spo2", "solunum", "isi", "hrv", "uyku", "egzersiz"]


def olcum_ekle(olcum: dict, ortam: str, zaman: str = None):
    with baglan() as b:
        b.execute(
            f"INSERT INTO olcumler (zaman, ortam, {', '.join(OLCUM_SUTUNLARI)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (zaman or simdi(), ortam, *[olcum[k] for k in OLCUM_SUTUNLARI]),
        )


def olcumleri_toplu_ekle(satirlar: list):
    """satirlar = [(zaman, ortam, nabiz, spo2, solunum, isi, hrv, uyku, egzersiz), ...]"""
    with baglan() as b:
        b.executemany(
            f"INSERT INTO olcumler (zaman, ortam, {', '.join(OLCUM_SUTUNLARI)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            satirlar,
        )


def son_olcum():
    return _satir("SELECT * FROM olcumler ORDER BY zaman DESC, id DESC LIMIT 1")


def son_olcumler(adet: int = 60) -> pd.DataFrame:
    df = _tablo("SELECT * FROM olcumler ORDER BY zaman DESC, id DESC LIMIT ?", (adet,))
    df = df.iloc[::-1].reset_index(drop=True)
    df["zaman"] = pd.to_datetime(df["zaman"])
    return df


def gunun_olcumleri(gun: str) -> pd.DataFrame:
    df = _tablo("SELECT * FROM olcumler WHERE zaman LIKE ? ORDER BY zaman", (gun + "%",))
    df["zaman"] = pd.to_datetime(df["zaman"])
    return df


def gunluk_ortalamalar(gun_sayisi: int = 14) -> pd.DataFrame:
    """Her gün için değerlerin ortalaması (grafikler sayfası için)."""
    baslangic = (date.today() - timedelta(days=gun_sayisi - 1)).isoformat()
    ortalamalar = ", ".join(f"AVG({k}) AS {k}" for k in OLCUM_SUTUNLARI if k != "egzersiz")
    df = _tablo(
        f"SELECT substr(zaman, 1, 10) AS gun, {ortalamalar}, MAX(egzersiz) AS egzersiz, COUNT(*) AS olcum_sayisi "
        f"FROM olcumler WHERE zaman >= ? GROUP BY gun ORDER BY gun",
        (baslangic,),
    )
    return df


def saatlik_ortalamalar(gun: str) -> pd.DataFrame:
    """Seçilen günün her saati için değerlerin ortalaması (00:00, 01:00, ...)."""
    ortalamalar = ", ".join(f"AVG({k}) AS {k}" for k in OLCUM_SUTUNLARI if k != "egzersiz")
    return _tablo(
        f"SELECT substr(zaman, 12, 2) || ':00' AS saat, {ortalamalar}, MAX(egzersiz) AS egzersiz, "
        f"COUNT(*) AS olcum_sayisi FROM olcumler WHERE zaman LIKE ? GROUP BY saat ORDER BY saat",
        (gun + "%",))


def olcum_gunleri() -> list:
    df = _tablo("SELECT DISTINCT substr(zaman, 1, 10) AS gun FROM olcumler ORDER BY gun DESC")
    return df["gun"].tolist()


def tum_olcumler() -> pd.DataFrame:
    return _tablo("SELECT * FROM olcumler ORDER BY zaman")


def olcumleri_sil():
    with baglan() as b:
        b.execute("DELETE FROM olcumler")


# ---------------------------------------------------------------
# RUH HALİ
# ---------------------------------------------------------------
def ruh_hali_ekle(ruh_hali, stres, enerji, yalnizlik, notu="", zaman=None):
    with baglan() as b:
        b.execute(
            "INSERT INTO ruh_hali (zaman, ruh_hali, stres, enerji, yalnizlik, notu) VALUES (?, ?, ?, ?, ?, ?)",
            (zaman or simdi(), ruh_hali, stres, enerji, yalnizlik, notu),
        )


def bugunku_ruh_hali():
    return _satir("SELECT * FROM ruh_hali WHERE zaman LIKE ? ORDER BY id DESC LIMIT 1", (bugun() + "%",))


def ruh_hali_gecmisi(gun: int = 14) -> pd.DataFrame:
    baslangic = (date.today() - timedelta(days=gun - 1)).isoformat()
    df = _tablo("SELECT * FROM ruh_hali WHERE zaman >= ? ORDER BY zaman", (baslangic,))
    df["zaman"] = pd.to_datetime(df["zaman"])
    return df


# ---------------------------------------------------------------
# GÖREVLER VE PUAN
# ---------------------------------------------------------------
def gorev_tamamla(gorev_kodu: str, puan: int, tarih: str = None) -> bool:
    """Görevi tamamlar. Aynı gün ikinci kez puan verilmez (False döner)."""
    try:
        with baglan() as b:
            b.execute("INSERT INTO tamamlanan_gorevler (tarih, gorev_kodu, puan) VALUES (?, ?, ?)",
                      (tarih or bugun(), gorev_kodu, puan))
        return True
    except sqlite3.IntegrityError:
        return False


def gorev_geri_al(gorev_kodu: str):
    """Bugün yanlışlıkla işaretlenen görevi geri alır (puanı da geri alınır)."""
    with baglan() as b:
        b.execute("DELETE FROM tamamlanan_gorevler WHERE tarih = ? AND gorev_kodu = ?", (bugun(), gorev_kodu))


def bugun_tamamlanan_gorevler() -> set:
    with baglan() as b:
        satirlar = b.execute("SELECT gorev_kodu FROM tamamlanan_gorevler WHERE tarih = ?", (bugun(),)).fetchall()
    return {s[0] for s in satirlar}


def toplam_puan() -> int:
    return int(_satir("SELECT COALESCE(SUM(puan), 0) AS p FROM tamamlanan_gorevler")["p"])


def seri_gun_sayisi() -> int:
    """Kaç gündür üst üste en az bir görev tamamlandı? (bugün henüz yapılmadıysa dünden sayar)"""
    with baglan() as b:
        gunler = {s[0] for s in b.execute("SELECT DISTINCT tarih FROM tamamlanan_gorevler").fetchall()}
    gun = date.today()
    if gun.isoformat() not in gunler:
        gun -= timedelta(days=1)
    seri = 0
    while gun.isoformat() in gunler:
        seri += 1
        gun -= timedelta(days=1)
    return seri


def gunluk_puanlar(gun_sayisi: int = 14) -> pd.DataFrame:
    """Son günlerde her gün kazanılan puan (görevler sayfasındaki grafik için)."""
    baslangic = (date.today() - timedelta(days=gun_sayisi - 1)).isoformat()
    return _tablo("SELECT tarih, SUM(puan) AS puan FROM tamamlanan_gorevler WHERE tarih >= ? "
                  "GROUP BY tarih ORDER BY tarih", (baslangic,))


def bugun_kazanilan_puan() -> int:
    return int(_satir("SELECT COALESCE(SUM(puan), 0) AS p FROM tamamlanan_gorevler WHERE tarih = ?",
                      (bugun(),))["p"])


# ---------------------------------------------------------------
# SU TAKİBİ (bugün içilen ml, ayarlar tablosunda tarihe göre saklanır)
# ---------------------------------------------------------------
def bugun_su_ml() -> int:
    return int(ayar(f"su_{bugun()}") or 0)


def su_ekle(ml: int) -> int:
    yeni = max(0, bugun_su_ml() + ml)
    ayar_kaydet(f"su_{bugun()}", yeni)
    return yeni


# ---------------------------------------------------------------
# GÜNLÜK (yazı / ses / video)
# ---------------------------------------------------------------
def dosya_kaydet(veri: bytes, uzanti: str) -> str:
    """Ses/video dosyasını 'kayitlar' klasörüne kaydeder ve yolunu döndürür."""
    os.makedirs(KAYIT_KLASORU, exist_ok=True)
    ad = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + "." + uzanti.lstrip(".")
    yol = os.path.join(KAYIT_KLASORU, ad)
    with open(yol, "wb") as f:
        f.write(veri)
    return yol


def gunluk_ekle(baslik, tur, metin, ruh_hali=None, dosya_yolu=None):
    with baglan() as b:
        b.execute(
            "INSERT INTO gunluk (zaman, baslik, tur, metin, ruh_hali, dosya_yolu) VALUES (?, ?, ?, ?, ?, ?)",
            (simdi(), baslik, tur, metin, ruh_hali, dosya_yolu),
        )


def gunluk_kayitlari() -> pd.DataFrame:
    df = _tablo("SELECT * FROM gunluk")
    df["zaman"] = pd.to_datetime(df["zaman"])
    return df


def gunluk_sil(kayit_id: int):
    s = _satir("SELECT dosya_yolu FROM gunluk WHERE id = ?", (kayit_id,))
    if s and s["dosya_yolu"] and os.path.exists(s["dosya_yolu"]):
        os.remove(s["dosya_yolu"])
    with baglan() as b:
        b.execute("DELETE FROM gunluk WHERE id = ?", (kayit_id,))


# ---------------------------------------------------------------
# PROFİL FOTOĞRAFI (kare kesilip 256 piksele küçültülür)
# ---------------------------------------------------------------
def profil_foto_kaydet(veri: bytes) -> str:
    import io
    from PIL import Image, ImageOps
    resim = ImageOps.exif_transpose(Image.open(io.BytesIO(veri))).convert("RGB")
    kenar = min(resim.size)
    sol, ust = (resim.width - kenar) // 2, (resim.height - kenar) // 2
    resim = resim.crop((sol, ust, sol + kenar, ust + kenar)).resize((256, 256))
    os.makedirs(KAYIT_KLASORU, exist_ok=True)
    yol = os.path.join(KAYIT_KLASORU, "profil_foto.jpg")
    resim.save(yol, quality=88)
    ayar_kaydet("profil_foto", yol)
    return yol


def profil_foto_yolu():
    yol = ayar("profil_foto")
    return yol if yol and os.path.exists(yol) else None


def profil_foto_sil():
    yol = profil_foto_yolu()
    if yol:
        os.remove(yol)
    ayar_kaydet("profil_foto", "")


# ---------------------------------------------------------------
# REGL DÖNGÜSÜ TAKİBİ (yalnızca kadın profillerde kullanılır)
# ---------------------------------------------------------------
def regl_donemleri() -> list:
    """Bütün dönemler, eskiden yeniye: [{"id", "baslangic", "bitis"}, ...]"""
    with baglan() as b:
        b.row_factory = sqlite3.Row
        return [dict(s) for s in b.execute("SELECT * FROM regl_donemleri ORDER BY baslangic").fetchall()]


def regl_baslat(tarih: str):
    """
    Yeni bir regl dönemi başlatır.
    - Daha önce başlamış ve hâlâ açık bir dönem varsa önce onu kapatır (en fazla 5 gün sürmüş sayılır).
    - Açık dönem bu tarihten sonra/aynı gün başlamış görünüyorsa, yanlış girilmiş başlangıcı düzeltir.
    """
    yeni = date.fromisoformat(tarih)
    with baglan() as b:
        acik = b.execute("SELECT id, baslangic FROM regl_donemleri WHERE bitis IS NULL").fetchall()
        for kayit_id, baslangic in acik:
            eski = date.fromisoformat(baslangic)
            if eski < yeni:
                bitis = min(yeni - timedelta(days=1), eski + timedelta(days=4))
                b.execute("UPDATE regl_donemleri SET bitis = ? WHERE id = ?", (bitis.isoformat(), kayit_id))
            else:  # başlangıç tarihi düzeltiliyor
                b.execute("UPDATE regl_donemleri SET baslangic = ? WHERE id = ?", (tarih, kayit_id))
                return
        if not b.execute("SELECT 1 FROM regl_donemleri WHERE baslangic = ?", (tarih,)).fetchone():
            b.execute("INSERT INTO regl_donemleri (baslangic, bitis) VALUES (?, NULL)", (tarih,))


def regl_bitir(tarih: str):
    with baglan() as b:
        b.execute("UPDATE regl_donemleri SET bitis = ? WHERE bitis IS NULL AND baslangic <= ?", (tarih, tarih))


def regl_donem_sil(kayit_id: int):
    with baglan() as b:
        b.execute("DELETE FROM regl_donemleri WHERE id = ?", (kayit_id,))


def regl_belirti_kaydet(tarih: str, akis: str, belirtiler: list, notu: str = ""):
    with baglan() as b:
        b.execute("INSERT OR REPLACE INTO regl_belirtileri (tarih, akis, belirtiler, notu) VALUES (?, ?, ?, ?)",
                  (tarih, akis, ",".join(belirtiler), notu))


def regl_belirtisi(tarih: str):
    s = _satir("SELECT * FROM regl_belirtileri WHERE tarih = ?", (tarih,))
    if s:
        s["belirtiler"] = [x for x in (s["belirtiler"] or "").split(",") if x]
    return s


def regl_belirti_gecmisi(gun_sayisi: int = 90) -> pd.DataFrame:
    baslangic = (date.today() - timedelta(days=gun_sayisi - 1)).isoformat()
    return _tablo("SELECT * FROM regl_belirtileri WHERE tarih >= ? ORDER BY tarih DESC", (baslangic,))


# ---------------------------------------------------------------
# DESTEK TALEPLERİ
# ---------------------------------------------------------------
def destek_talebi_ekle(tur: str, notu: str = ""):
    with baglan() as b:
        b.execute("INSERT INTO destek_talepleri (zaman, tur, notu) VALUES (?, ?, ?)", (simdi(), tur, notu))


def destek_talepleri() -> pd.DataFrame:
    return _tablo("SELECT * FROM destek_talepleri ORDER BY id DESC LIMIT 10")


# ---------------------------------------------------------------
# SOHBET (yapay zeka asistanı)
# ---------------------------------------------------------------
def sohbet_ekle(rol: str, metin: str):
    with baglan() as b:
        b.execute("INSERT INTO sohbet (zaman, rol, metin) VALUES (?, ?, ?)", (simdi(), rol, metin))


def sohbet_gecmisi(adet: int = 40) -> list:
    df = _tablo("SELECT rol, metin FROM sohbet ORDER BY id DESC LIMIT ?", (adet,))
    return df.iloc[::-1].to_dict("records")


def sohbeti_temizle():
    with baglan() as b:
        b.execute("DELETE FROM sohbet")


# ---------------------------------------------------------------
# TÜMÜNÜ SİL
# ---------------------------------------------------------------
def her_seyi_sil():
    with baglan() as b:
        for tablo in ["profil", "olcumler", "ruh_hali", "tamamlanan_gorevler", "gunluk",
                      "destek_talepleri", "sohbet", "ayarlar", "regl_donemleri", "regl_belirtileri"]:
            b.execute(f"DELETE FROM {tablo}")
