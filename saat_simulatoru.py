"""
SAAT SİMÜLATÖRÜ — Gerçek akıllı saat olmadığı için onu taklit ediyoruz.

Gerçek hayatta bu dosyanın yerine saatten veri okuyan kod gelir.
Değerler rastgele zıplamaz; seçilen senaryonun hedefine doğru yavaşça kayar.
"""
import random
from datetime import datetime, timedelta

import ayarlar
import veritabani


def _yaklas(eski, hedef, oran=0.25, gurultu=1.0):
    return eski + (hedef - eski) * oran + random.gauss(0, gurultu)


def yeni_olcum_uret(senaryo: str) -> dict:
    hedef = ayarlar.SENARYOLAR[senaryo]["hedef"]
    onceki = veritabani.son_olcum()
    if onceki is None or not onceki["zaman"].startswith(veritabani.bugun()):
        # Günün ilk ölçümü: uyku yeni hesaplanır, egzersiz sıfırdan değil örnek bir değerden başlar
        temel = dict(hedef)
        temel["egzersiz"] = 60  # gün ortası gibi: egzersizin yarısı yapılmış
        if onceki is None:
            onceki = temel
        else:
            onceki = {**onceki, "egzersiz": temel["egzersiz"]}

    yeni = {
        "nabiz": round(_yaklas(onceki["nabiz"], hedef["nabiz"], gurultu=2.0)),
        "spo2": round(min(100, _yaklas(onceki["spo2"], hedef["spo2"], gurultu=0.4))),
        "solunum": round(_yaklas(onceki["solunum"], hedef["solunum"], gurultu=0.6)),
        "isi": round(_yaklas(onceki["isi"], hedef["isi"], gurultu=0.03), 1),
        "hrv": round(max(5, _yaklas(onceki["hrv"], hedef["hrv"], gurultu=1.5))),
        "uyku": hedef["uyku"],
        # egzersiz senaryosunda geçen süre kadar dakika eklenir (sunumda kısa aralıkta en az 3 dk)
        "egzersiz": onceki["egzersiz"] + (max(3, int(veritabani.ayar("olcum_araligi")) // 60)
                                          if senaryo == "egzersiz" else 0),
    }
    return yeni


def olcum_zamani_geldi_mi(saniye: int = 4) -> bool:
    son = veritabani.son_olcum()
    if son is None:
        return True
    gecen = datetime.now() - datetime.strptime(son["zaman"], "%Y-%m-%d %H:%M:%S")
    return gecen.total_seconds() >= saniye


def olcum_al_ve_kaydet(senaryo: str, ortam: str) -> dict:
    olcum = yeni_olcum_uret(senaryo)
    veritabani.olcum_ekle(olcum, ortam)
    return olcum


def gecmis_veri_uret(gun_sayisi: int = 14, ortam: str = "iss"):
    """
    Sunum için son günlere ait gerçekçi örnek veri üretir:
    her 30 dakikada bir ölçüm, gece nabız düşük, gündüz egzersiz artıyor.
    Ayrıca ruh hali kayıtları ve tamamlanmış görevler de ekler.
    """
    satirlar = []
    simdi = datetime.now().replace(second=0, microsecond=0)
    for g in range(gun_sayisi, 0, -1):
        gun = (simdi - timedelta(days=g)).replace(hour=0, minute=0)
        uyku = round(random.uniform(5.4, 8.2), 1)
        egzersiz = 0
        hrv_gun = random.uniform(32, 62)
        for adim in range(48):
            an = gun + timedelta(minutes=30 * adim)
            saat = an.hour + an.minute / 60
            uyanik = 7 <= saat < 23
            egzersiz_saati = 10 <= saat < 11.5 or 16 <= saat < 17
            if egzersiz_saati:
                egzersiz += random.randint(12, 18)
            nabiz = (58 if not uyanik else 72) + (45 if egzersiz_saati else 0) + random.gauss(0, 3)
            satirlar.append((
                an.strftime("%Y-%m-%d %H:%M:%S"), ortam,
                round(nabiz),
                round(min(100, random.gauss(97.5, 0.8))),
                round((13 if not uyanik else 15) + (8 if egzersiz_saati else 0) + random.gauss(0, 1)),
                round(random.gauss(36.6, 0.15) + (0.6 if egzersiz_saati else 0), 1),
                round(max(10, hrv_gun + (8 if not uyanik else 0) - (15 if egzersiz_saati else 0)
                          + random.gauss(0, 3))),
                uyku,
                egzersiz,
            ))
        tarih = gun.date().isoformat()
        veritabani.ruh_hali_ekle(random.randint(3, 5), random.randint(2, 7), random.randint(2, 5),
                                 random.randint(1, 4), "", zaman=f"{tarih} 21:00:00")
        for gorev in random.sample(ayarlar.GOREVLER, k=random.randint(2, 5)):
            veritabani.gorev_tamamla(gorev["kod"], gorev["puan"], tarih=tarih)
    veritabani.olcumleri_toplu_ekle(satirlar)
    return len(satirlar)
