"""
AYARLAR — Uygulamanın tüm "bilgisi" burada.

Hangi değerleri izlediğimiz, hangi aralığın normal olduğu ve
astronota ne söyleyeceğimiz bu dosyada yazılı.
Yeni bir değer eklemek ya da bir sınırı değiştirmek için SADECE bu dosyayı değiştir.

Yazılar birden fazla dilde: {"tr": "...", "en": "..."}
Bir dilde yazı yoksa İngilizcesi gösterilir.

DİKKAT: Sınırlar şimdilik örnek değerlerdir. Analiz yapan arkadaşınız
NASA verilerine göre bunları güncelleyecek.
"""


def L(tr, en, es=None, ru=None):
    """Çok dilli yazı oluşturur. es/ru verilmezse İngilizce kullanılır."""
    d = {"tr": tr, "en": en}
    if es:
        d["es"] = es
    if ru:
        d["ru"] = ru
    return d


# ---------------------------------------------------------------
# RENKLER (trafik ışığı mantığı)
# ---------------------------------------------------------------
RENKLER = {"yesil": "#22c55e", "sari": "#facc15", "kirmizi": "#ef4444"}

DURUM_YAZILARI = {
    "yesil": L("NORMAL", "NORMAL", "NORMAL", "НОРМА"),
    "sari": L("DİKKAT", "CAUTION", "PRECAUCIÓN", "ВНИМАНИЕ"),
    "kirmizi": L("ACİL", "URGENT", "URGENTE", "СРОЧНО"),
}

# Kırmızı durumda her mesajın sonuna eklenir. Uygulama doktorun yerine geçmez.
DOKTORA_HABER_VER = L(
    "Bu adımlardan sonra 10 dakika içinde düzelmezse uçuş doktoruna (Flight Surgeon) hemen haber ver.",
    "If it does not improve within 10 minutes after these steps, contact the Flight Surgeon immediately.",
    "Si no mejora en 10 minutos después de estos pasos, contacta de inmediato al médico de vuelo (Flight Surgeon).",
    "Если в течение 10 минут после этих шагов не станет лучше, немедленно свяжитесь с полётным врачом.",
)

# ---------------------------------------------------------------
# İZLENEN DEĞERLER
# yesil: (en az, en çok) -> NORMAL   |  sari: (en az, en çok) -> DİKKAT  |  dışı -> ACİL
# ---------------------------------------------------------------
METRIKLER = {
    "nabiz": {
        "ad": L("Kalp Ritmi", "Heart Rate", "Frecuencia cardíaca", "Пульс"),
        "birim": "bpm", "ikon": "kalp", "bolge": "kalp",
        "yesil": (50, 100), "sari": (40, 120),
        "ne_demek": L("Kalbinin bir dakikada kaç kez attığını gösterir.",
                      "Shows how many times your heart beats per minute."),
        "nasil_olculur": L("Saat bileğine sıkıca otursun. 1 dakika kıpırdamadan otur ve saatteki değeri bekle.",
                           "Wear the watch snugly. Sit still for 1 minute and wait for the reading."),
        "mesajlar": {
            "yesil": (L("Kalp ritmin normal", "Your heart rate is normal"),
                      L("Bir şey yapmana gerek yok. Böyle devam et.", "No action needed. Keep it up.")),
            "sari": (L("Nabzın normal aralığın dışında", "Your heart rate is outside the normal range"),
                     L("Egzersiz yapıyorsan bu beklenebilir. Yapmıyorsan 5 dakika otur, yavaş nefes al ve tekrar ölç.",
                       "This can be expected during exercise. If you are not exercising, sit for 5 minutes, "
                       "breathe slowly and measure again.")),
            "kirmizi": (L("Nabzın çok yüksek ya da çok düşük", "Your heart rate is very high or very low"),
                        L("Yaptığın işi hemen bırak ve otur. Yavaş ve derin nefes al. 5 dakika sonra tekrar ölç.",
                          "Stop what you are doing and sit down. Breathe slowly and deeply. Measure again in 5 minutes.")),
        },
    },
    "spo2": {
        "ad": L("Kan Oksijeni", "Blood Oxygen", "Oxígeno en sangre", "Кислород крови"),
        "birim": "%", "ikon": "damla", "bolge": "akciger",
        "yesil": (95, 100), "sari": (92, 100),
        "ne_demek": L("Kanındaki oksijen oranıdır. Akciğerlerinin vücuda ne kadar oksijen taşıdığını gösterir.",
                      "The oxygen level in your blood. Shows how well your lungs deliver oxygen to your body."),
        "nasil_olculur": L("Saati bilek kemiğinin 2 parmak yukarısına tak. Elini kalp hizasında hareketsiz tut.",
                           "Wear the watch two fingers above the wrist bone. Keep your hand still at heart level."),
        "mesajlar": {
            "yesil": (L("Oksijen seviyen normal", "Your oxygen level is normal"),
                      L("Bir şey yapmana gerek yok.", "No action needed.")),
            "sari": (L("Oksijen seviyen biraz düşük", "Your oxygen level is slightly low"),
                     L("Otur ve 2 dakika derin nefes al. Kabin havası göstergesini kontrol et, sonra tekrar ölç.",
                       "Sit down and breathe deeply for 2 minutes. Check the cabin air display, then measure again.")),
            "kirmizi": (L("Oksijen seviyen tehlikeli derecede düşük", "Your oxygen level is dangerously low"),
                        L("Hemen dur ve otur. Kabin oksijen/CO2 göstergesine bak. Gerekirse oksijen maskesini kullan "
                          "ve ekip arkadaşına haber ver.",
                          "Stop and sit down now. Check the cabin O2/CO2 display. Use the oxygen mask if needed "
                          "and tell a crewmate.")),
        },
    },
    "solunum": {
        "ad": L("Solunum Hızı", "Respiratory Rate", "Frecuencia respiratoria", "Частота дыхания"),
        "birim": L("nefes/dk", "breaths/min", "resp/min", "вдох/мин"), "ikon": "ruzgar", "bolge": "akciger",
        "yesil": (12, 20), "sari": (9, 24),
        "ne_demek": L("Bir dakikada kaç kez nefes aldığını gösterir.", "How many breaths you take per minute."),
        "nasil_olculur": L("Saat bunu otomatik ölçer. Ölçüm sırasında konuşma.",
                           "The watch measures this automatically. Do not talk during the measurement."),
        "mesajlar": {
            "yesil": (L("Nefes alışın normal", "Your breathing is normal"),
                      L("Bir şey yapmana gerek yok.", "No action needed.")),
            "sari": (L("Nefes alışın normalden farklı", "Your breathing is unusual"),
                     L("Otur. 4 saniye nefes al, 4 saniye tut, 4 saniye ver. Bunu 3 dakika yap.",
                       "Sit down. Breathe in for 4 seconds, hold for 4, breathe out for 4. Do this for 3 minutes.")),
            "kirmizi": (L("Nefes alışın çok hızlı ya da çok yavaş", "Your breathing is very fast or very slow"),
                        L("Hemen dur ve otur. Nefes darlığın varsa ekip arkadaşına haber ver.",
                          "Stop and sit down now. If you feel short of breath, tell a crewmate.")),
        },
    },
    "isi": {
        "ad": L("Vücut Isısı", "Body Temperature", "Temperatura corporal", "Температура тела"),
        "birim": "°C", "ikon": "termometre", "bolge": "genel",
        "yesil": (36.1, 37.4), "sari": (35.5, 38.0),
        "ne_demek": L("Vücudunun sıcaklığıdır. Yüksekse ateş, düşükse üşüme olabilir.",
                      "Your body temperature. High may mean fever, low may mean you are too cold."),
        "nasil_olculur": L("Saat otomatik ölçer. Egzersizden hemen sonra yüksek çıkabilir, 15 dakika bekle.",
                           "Measured automatically. It may read high right after exercise; wait 15 minutes."),
        "mesajlar": {
            "yesil": (L("Vücut ısın normal", "Your temperature is normal"),
                      L("Bir şey yapmana gerek yok.", "No action needed.")),
            "sari": (L("Vücut ısın normalden farklı", "Your temperature is outside normal"),
                     L("Egzersizden sonraysa 15 dakika dinlen ve su iç. Değilse 30 dakika sonra tekrar ölç.",
                       "If after exercise, rest for 15 minutes and drink water. Otherwise measure again in 30 minutes.")),
            "kirmizi": (L("Vücut ısın çok yüksek ya da çok düşük", "Your temperature is very high or very low"),
                        L("Dinlen, su iç. İlk yardım çantasındaki termometreyle tekrar ölç.",
                          "Rest and drink water. Measure again with the thermometer in the medical kit.")),
        },
    },
    "hrv": {
        "ad": L("Stres Göstergesi (HRV)", "Stress Indicator (HRV)", "Indicador de estrés (VFC)",
                "Индикатор стресса (ВСР)"),
        "birim": "ms", "ikon": "beyin", "bolge": "beyin",
        "yesil": (40, 200), "sari": (25, 200),
        "normal_yazi": L("40 ve üzeri", "40 or higher", "40 o más", "40 и выше"),
        "ne_demek": L("Kalp atışların arasındaki küçük farklardır. Yüksek olması iyidir; düşük olması stres veya "
                      "yorgunluk olabileceğini gösterir.",
                      "Small differences between heartbeats. Higher is better; low values can signal stress or fatigue."),
        "nasil_olculur": L("Saat dinlenirken ve uyurken ölçer. Sabah uyanınca bakmak en doğrusudur.",
                           "Measured at rest and during sleep. Best checked right after waking up."),
        "mesajlar": {
            "yesil": (L("Stres seviyen düşük", "Your stress level is low"),
                      L("Vücudun iyi dinleniyor.", "Your body is recovering well.")),
            "sari": (L("Stres seviyen artıyor", "Your stress level is rising"),
                     L("10 dakika ara ver. Pencereden Dünya'ya bak veya sevdiğin bir müziği dinle.",
                       "Take a 10-minute break. Look at Earth from the window or listen to music you like.")),
            "kirmizi": (L("Stres seviyen çok yüksek", "Your stress level is very high"),
                        L("Görevine kısa bir ara ver. 10 dakika 4-7-8 nefes egzersizi yap. Bugün mürettebat "
                          "psikoloğuyla görüşme planla.",
                          "Take a short break. Do 4-7-8 breathing for 10 minutes. Schedule a talk with the crew "
                          "psychologist today.")),
        },
    },
    "uyku": {
        "ad": L("Uyku Süresi", "Sleep Duration", "Duración del sueño", "Продолжительность сна"),
        "birim": L("saat", "h", "h", "ч"), "ikon": "ay", "bolge": "beyin",
        "yesil": (7.0, 12.0), "sari": (6.0, 12.0),
        "normal_yazi": L("7 saat ve üzeri", "7 hours or more", "7 horas o más", "7 часов и более"),
        "ne_demek": L("Dün gece ne kadar uyuduğunu gösterir. Az uyku dikkatini ve kararlarını etkiler.",
                      "How long you slept last night. Too little sleep affects attention and decisions."),
        "nasil_olculur": L("Saati uyurken takılı tut. Sabah otomatik hesaplanır.",
                           "Keep the watch on while sleeping. It is calculated automatically in the morning."),
        "mesajlar": {
            "yesil": (L("Yeterince uyudun", "You slept enough"),
                      L("Uyku düzenini koru.", "Keep your sleep routine.")),
            "sari": (L("Uykun biraz az", "Your sleep was a bit short"),
                     L("Bu akşam uyku saatinden 1 saat önce ekranları kapat ve kabin ışığını kıs.",
                       "Tonight, turn off screens and dim the cabin light 1 hour before bed.")),
            "kirmizi": (L("Çok az uyudun", "You slept very little"),
                        L("Bugün riskli işler (uzay yürüyüşü, robot kol) için ekip arkadaşından destek iste. "
                          "Uygunsa 20 dakika kestir.",
                          "Ask a crewmate for support with risky tasks today (EVA, robotic arm). "
                          "Take a 20-minute nap if possible.")),
        },
    },
    "egzersiz": {
        "ad": L("Günlük Egzersiz", "Daily Exercise", "Ejercicio diario", "Ежедневные упражнения"),
        "birim": L("dk", "min", "min", "мин"), "ikon": "egzersiz", "bolge": "kaslar",
        "yesil": (90, 600), "sari": (45, 600),
        "normal_yazi": L("90 dk ve üzeri", "90 min or more", "90 min o más", "90 мин и более"),
        "ne_demek": L("Bugün yaptığın egzersiz süresi. Uzayda yerçekimi az olduğu için egzersiz yapmazsan "
                      "kasların ve kemiklerin zayıflar.",
                      "Your exercise time today. With low gravity, muscles and bones weaken without exercise."),
        "nasil_olculur": L("Egzersize başlarken saatte 'Antrenman' modunu aç.",
                           "Turn on 'Workout' mode on the watch when you start."),
        "mesajlar": {
            "yesil": (L("Günlük egzersizini tamamladın", "Daily exercise complete"),
                      L("Kasların ve kemiklerin korunuyor.", "Your muscles and bones are protected.")),
            "sari": (L("Egzersizin yarıda kaldı", "Exercise is half done"),
                     L("Bugün 30-45 dakika daha egzersiz yap (koşu bandı veya direnç aleti).",
                       "Do 30-45 more minutes today (treadmill or resistance device).")),
            "kirmizi": (L("Bugün çok az egzersiz yaptın", "Very little exercise today"),
                        L("Kas ve kemik kaybını önlemek için bugün en az 1 saat egzersiz planla.",
                          "Plan at least 1 hour of exercise today to prevent muscle and bone loss.")),
        },
    },
}

# ---------------------------------------------------------------
# VÜCUT BÖLGELERİ
# ---------------------------------------------------------------
BOLGELER = {
    "beyin": L("Beyin ve uyku", "Brain and sleep", "Cerebro y sueño", "Мозг и сон"),
    "kalp": L("Kalp ve dolaşım", "Heart and circulation", "Corazón y circulación", "Сердце и кровообращение"),
    "akciger": L("Akciğer ve solunum", "Lungs and breathing", "Pulmones y respiración", "Лёгкие и дыхание"),
    "kaslar": L("Kas ve kemik", "Muscle and bone", "Músculo y hueso", "Мышцы и кости"),
    "genel": L("Vücut ısısı (termal)", "Body heat (thermal)", "Calor corporal (térmico)", "Температура (тепловая)"),
    "radyasyon": L("Radyasyon (tüm vücut)", "Radiation (whole body)", "Radiación (cuerpo entero)",
                   "Радиация (всё тело)"),
}

# ---------------------------------------------------------------
# RADYASYON
# Kümülatif doz = görev günü x ortamın günlük dozu.
# NASA'nın kariyer boyu etkin doz sınırı 600 mSv'dir; yarısında uyarı veriyoruz.
# ---------------------------------------------------------------
RADYASYON_UYARI = 300   # mSv
RADYASYON_KRITIK = 600  # mSv

# ---------------------------------------------------------------
# SAATTEN VERİ ALMA ARALIĞI (saniye). Varsayılan: 3 dakika.
# Kısa aralıklar sunumda canlı değişimi göstermek içindir.
# ---------------------------------------------------------------
OLCUM_ARALIKLARI = [5, 30, 60, 180, 300, 600]
VARSAYILAN_OLCUM_ARALIGI = 180

# ---------------------------------------------------------------
# SU TAKİBİ (günlük görev)
# ---------------------------------------------------------------
SU_HEDEF_ML = 2000
BARDAK_ML = 250

# ---------------------------------------------------------------
# GÖREV ORTAMLARI
# radyasyon: yaklaşık günlük doz (mSv/gün), yercekimi: Dünya'ya göre (g)
# Değerler yaklaşık ve gösterim amaçlıdır.
# ---------------------------------------------------------------
ORTAMLAR = {
    "iss": {"ad": L("Uluslararası Uzay İstasyonu", "International Space Station",
                    "Estación Espacial Internacional", "Международная космическая станция"),
            "kisa": "ISS", "radyasyon": 0.5, "yercekimi": 0.0, "co2": 0.35, "kabin": 22.5,
            "not": L("Mikro yerçekimi: kas ve kemik kaybına dikkat. Günlük egzersizini atlama.",
                     "Microgravity: watch for muscle and bone loss. Do not skip daily exercise.")},
    "ay": {"ad": L("Ay Üssü", "Lunar Base", "Base lunar", "Лунная база"),
           "kisa": "ARTEMIS", "radyasyon": 1.4, "yercekimi": 0.17, "co2": 0.30, "kabin": 21.5,
           "not": L("Ay yerçekimi Dünya'nın 1/6'sı. Toz ve radyasyona karşı dikkatli ol.",
                    "Lunar gravity is 1/6 of Earth's. Be careful with dust and radiation.")},
    "mars": {"ad": L("Mars Üssü", "Mars Base", "Base en Marte", "База на Марсе"),
             "kisa": "MARS", "radyasyon": 0.7, "yercekimi": 0.38, "co2": 0.30, "kabin": 21.0,
             "not": L("Dünya ile mesajlaşma 40 dakikaya kadar gecikebilir. Acil durumda önce ekibinle hareket et.",
                      "Messages to Earth can take up to 40 minutes. In an emergency, act with your crew first.")},
    "transit": {"ad": L("Derin Uzay Transit", "Deep Space Transit", "Tránsito al espacio profundo",
                        "Перелёт в дальнем космосе"),
                "kisa": "ORION", "radyasyon": 1.8, "yercekimi": 0.0, "co2": 0.40, "kabin": 22.4,
                "not": L("Dünya'dan çok uzaktasın. Rutinlerini korumak ruh sağlığın için önemli.",
                         "You are far from Earth. Keeping routines matters for your mental health.")},
    "rover": {"ad": L("Keşif Aracı (Rover)", "Exploration Rover", "Vehículo explorador", "Планетоход"),
              "kisa": "ROVER", "radyasyon": 1.4, "yercekimi": 0.17, "co2": 0.45, "kabin": 20.5,
              "not": L("Dar alanda uzun süre kalıyorsun. Her 2 saatte bir esneme hareketi yap.",
                       "You are in a small space for long hours. Stretch every 2 hours.")},
}

# ---------------------------------------------------------------
# SİMÜLASYON SENARYOLARI (sunumda jüriye göstermek için)
# ---------------------------------------------------------------
SENARYOLAR = {
    "normal": {"ad": L("Normal gün", "Normal day", "Día normal", "Обычный день"),
               "hedef": {"nabiz": 70, "spo2": 98, "solunum": 14, "isi": 36.7, "hrv": 55, "uyku": 7.6}},
    "egzersiz": {"ad": L("Yoğun egzersiz", "Intense exercise", "Ejercicio intenso", "Интенсивная тренировка"),
                 "hedef": {"nabiz": 138, "spo2": 96, "solunum": 26, "isi": 37.7, "hrv": 30, "uyku": 7.6}},
    "uykusuz": {"ad": L("Uyku eksikliği", "Sleep deprivation", "Falta de sueño", "Недосып"),
                "hedef": {"nabiz": 84, "spo2": 97, "solunum": 16, "isi": 36.8, "hrv": 30, "uyku": 4.6}},
    "oksijen": {"ad": L("Kabin oksijen sorunu", "Cabin oxygen problem", "Problema de oxígeno en cabina",
                        "Проблема с кислородом"),
                "hedef": {"nabiz": 108, "spo2": 89, "solunum": 25, "isi": 36.9, "hrv": 32, "uyku": 7.2}},
    "stres": {"ad": L("Yüksek stres", "High stress", "Estrés alto", "Сильный стресс"),
              "hedef": {"nabiz": 96, "spo2": 98, "solunum": 20, "isi": 37.0, "hrv": 21, "uyku": 6.3}},
}

# ---------------------------------------------------------------
# GÜNLÜK GÖREVLER (OYUNLAŞTIRMA)
# otomatik=True olanlar uygulamada ilgili işlem yapılınca kendiliğinden tamamlanır.
# hedef: bildirime tıklanınca gidilecek yer -> ("sayfa", dosya) | ("bolge", vücut bölgesi) | ("gorev", görev kodu)
# ---------------------------------------------------------------
GOREVLER = [
    {"kod": "sabah_nabiz", "ikon": "kalp", "hedef": ("bolge", "kalp"), "etkilesim": "olcum", "puan": 20, "otomatik": False,
     "ad": L("Sabah dinlenme nabzını ölç", "Measure resting heart rate in the morning",
             "Mide tu pulso en reposo por la mañana", "Измерьте пульс в покое утром"),
     "aciklama": L("Uyanınca yataktan kalkmadan 1 dakika hareketsiz kal ve nabzını ölç.",
                   "After waking, stay still for 1 minute before getting up and measure.")},
    {"kod": "su", "ikon": "damla", "hedef": ("gorev", "su"), "etkilesim": "su", "puan": 20, "otomatik": False,
     "ad": L("En az 2 litre su iç", "Drink at least 2 liters of water", "Bebe al menos 2 litros de agua",
             "Выпейте не менее 2 литров воды"),
     "aciklama": L("Uzayda susama hissi azalır. Su torbanı her öğünde doldur.",
                   "Thirst is weaker in space. Refill your water pouch at every meal.")},
    {"kod": "egzersiz", "ikon": "egzersiz", "hedef": ("gorev", "egzersiz"), "etkilesim": "egzersiz", "puan": 50, "otomatik": True,
     "ad": L("Günlük egzersizini tamamla", "Complete your daily exercise", "Completa tu ejercicio diario",
             "Выполните ежедневную тренировку"),
     "aciklama": L("Koşu bandı ve direnç aleti, toplam en az 90 dakika. Saat 90 dakikayı görünce kendiliğinden tamamlanır.",
                   "Treadmill and resistance device, at least 90 minutes in total. Completes automatically "
                   "when the watch records 90 minutes.")},
    {"kod": "ruh_hali", "ikon": "beyin", "hedef": ("sayfa", "sayfalar/destek.py"), "etkilesim": "sayfa_destek", "puan": 30, "otomatik": True,
     "ad": L("Ruh hali kontrolünü doldur", "Complete the mood check-in", "Completa el control de ánimo",
             "Заполните проверку настроения"),
     "aciklama": L("Güvenlik ve Yardım sayfasındaki 4 kısa soruyu cevapla.",
                   "Answer the 4 short questions on the Safety and Support page.")},
    {"kod": "nefes", "ikon": "ruzgar", "hedef": ("sayfa", "sayfalar/destek.py"), "etkilesim": "nefes", "puan": 20, "otomatik": False,
     "ad": L("5 dakika nefes egzersizi yap", "Do 5 minutes of breathing exercise",
             "Haz 5 minutos de respiración", "Сделайте 5 минут дыхательной гимнастики"),
     "aciklama": L("4 saniye nefes al, 7 saniye tut, 8 saniye ver. 5 dakika tekrarla.",
                   "Breathe in for 4 seconds, hold for 7, out for 8. Repeat for 5 minutes.")},
    {"kod": "gunluk", "ikon": "kitap", "hedef": ("sayfa", "sayfalar/gunluk.py"), "etkilesim": "sayfa_gunluk", "puan": 20, "otomatik": True,
     "ad": L("Günlüğüne bir kayıt ekle", "Add a journal entry", "Añade una entrada al diario",
             "Добавьте запись в дневник"),
     "aciklama": L("Yazı, ses veya video olarak bugününü kaydet.",
                   "Record your day as text, audio or video.")},
    {"kod": "aile", "ikon": "telefon", "hedef": ("sayfa", "sayfalar/destek.py"), "etkilesim": "onay", "puan": 30, "otomatik": False,
     "ad": L("Ailenle ya da bir arkadaşınla konuş", "Talk to family or a friend", "Habla con tu familia o un amigo",
             "Поговорите с семьёй или другом"),
     "aciklama": L("Sevdiklerinle konuşmak yalnızlık hissini azaltır.",
                   "Talking to loved ones reduces loneliness.")},
]

SEVIYE_PUANI = 200
SEVIYE_UNVANLARI = [
    L("Çaylak Astronot", "Rookie Astronaut", "Astronauta novato", "Новичок"),
    L("Yörünge Gezgini", "Orbit Explorer", "Explorador orbital", "Орбитальный исследователь"),
    L("Ay Kaşifi", "Moon Pioneer", "Pionero lunar", "Лунный первопроходец"),
    L("Mars Öncüsü", "Mars Vanguard", "Vanguardia de Marte", "Покоритель Марса"),
    L("Galaksi Kaptanı", "Galaxy Captain", "Capitán galáctico", "Капитан галактики"),
]

# ---------------------------------------------------------------
# KAYIT ANKETİ SEÇENEKLERİ
# ---------------------------------------------------------------
UNVANLAR = ["Astronot", "Komutan", "Uçuş Mühendisi", "Görev Uzmanı", "Uçuş Doktoru", "Bilim İnsanı"]
UNVAN_CEVIRI = {
    "Astronot": L("Astronot", "Astronaut", "Astronauta", "Космонавт"),
    "Komutan": L("Komutan", "Commander", "Comandante", "Командир"),
    "Uçuş Mühendisi": L("Uçuş Mühendisi", "Flight Engineer", "Ingeniero de vuelo", "Бортинженер"),
    "Görev Uzmanı": L("Görev Uzmanı", "Mission Specialist", "Especialista de misión", "Специалист миссии"),
    "Uçuş Doktoru": L("Uçuş Doktoru", "Flight Surgeon", "Médico de vuelo", "Полётный врач"),
    "Bilim İnsanı": L("Bilim İnsanı", "Scientist", "Científico", "Учёный"),
}
KAN_GRUPLARI = ["Bilinmiyor", "0+", "0-", "A+", "A-", "B+", "B-", "AB+", "AB-"]

# ---------------------------------------------------------------
# RUH SAĞLIĞI: KONULAR VE EGZERSİZLER (Güvenlik ve Yardım sayfası)
# ---------------------------------------------------------------
RUH_HALI_SECENEKLERI = {
    1: L("Çok kötü", "Very bad", "Muy mal", "Очень плохо"),
    2: L("Kötü", "Bad", "Mal", "Плохо"),
    3: L("İdare eder", "Okay", "Regular", "Нормально"),
    4: L("İyi", "Good", "Bien", "Хорошо"),
    5: L("Çok iyi", "Very good", "Muy bien", "Отлично"),
}

EGZERSIZLER = [
    {"ad": L("4-7-8 Nefes", "4-7-8 Breathing", "Respiración 4-7-8", "Дыхание 4-7-8"),
     "sure": L("5 dakika", "5 minutes", "5 minutos", "5 минут"),
     "adimlar": L(["Rahat bir şekilde otur veya kendini bir yere sabitle.",
                   "Burnundan 4 saniye boyunca nefes al.",
                   "Nefesini 7 saniye tut.",
                   "Ağzından 8 saniye boyunca yavaşça ver.",
                   "Bunu 4-5 kez tekrarla. Başın dönerse normal nefese dön."],
                  ["Sit comfortably or anchor yourself.",
                   "Breathe in through your nose for 4 seconds.",
                   "Hold your breath for 7 seconds.",
                   "Breathe out slowly through your mouth for 8 seconds.",
                   "Repeat 4-5 times. If you feel dizzy, return to normal breathing."])},
    {"ad": L("5-4-3-2-1 Topraklanma", "5-4-3-2-1 Grounding", "Anclaje 5-4-3-2-1", "Заземление 5-4-3-2-1"),
     "sure": L("3 dakika", "3 minutes", "3 minutos", "3 минуты"),
     "adimlar": L(["Gördüğün 5 şeyi say.", "Dokunabildiğin 4 şeyi say.", "Duyduğun 3 sesi say.",
                   "Kokusunu alabildiğin 2 şeyi say.", "Tadını alabildiğin 1 şeyi düşün.",
                   "Kaygı anında zihnini şimdiye getirir."],
                  ["Name 5 things you can see.", "Name 4 things you can touch.", "Name 3 sounds you hear.",
                   "Name 2 things you can smell.", "Think of 1 thing you can taste.",
                   "This brings your mind back to the present during anxiety."])},
    {"ad": L("Kas Gevşetme", "Muscle Relaxation", "Relajación muscular", "Мышечная релаксация"),
     "sure": L("10 dakika", "10 minutes", "10 minutos", "10 минут"),
     "adimlar": L(["Ayak parmaklarından başla: 5 saniye sık, sonra 10 saniye gevşet.",
                   "Sırasıyla bacaklar, karın, eller, kollar, omuzlar ve yüz için tekrarla.",
                   "Gevşeme hissine odaklan.",
                   "Uyumadan önce yapmak uykuya geçişi kolaylaştırır."],
                  ["Start with your toes: tense for 5 seconds, then relax for 10.",
                   "Repeat for legs, belly, hands, arms, shoulders and face.",
                   "Focus on the feeling of relaxation.",
                   "Doing this before bed makes falling asleep easier."])},
]

KONULAR = [
    {"kod": "yalnizlik", "ad": L("Aileni ve Dünya'yı özlemek", "Missing family and Earth",
                                 "Extrañar a la familia y la Tierra", "Тоска по семье и Земле"),
     "aciklama": L("Aylarca ailenden, arkadaşlarından ve Dünya'dan uzakta yaşamak özlem yaratır. Bu, uzun görevlerde "
                   "en sık yaşanan duygudur ve çok normaldir. Doğum günleri, bayramlar ve özel günlerde daha güçlü "
                   "hissedilebilir.",
                   "Living away from family, friends and Earth for months creates longing. It is the most common "
                   "feeling on long missions and completely normal. It can feel stronger on birthdays and holidays."),
     "adimlar": L(["Haftada en az bir kez ailenle görüntülü görüşme planla; görüşme saatini önceden belirle.",
                   "Ailene günlüğünden sesli veya görüntülü mesaj kaydet.",
                   "Evden getirdiğin fotoğraflara ve eşyalara bak; kabinine birkaç fotoğraf as.",
                   "Pencereden Dünya'yı izle ve memleketinin üzerinden geçişini takip et.",
                   "Özel günleri ekip arkadaşlarınla birlikte kutla.",
                   "Ekip arkadaşlarınla yemekleri birlikte ye ve sohbet et."],
                  ["Schedule a video call with family at least once a week; set the time in advance.",
                   "Record a voice or video message for your family in your journal.",
                   "Look at photos and items from home; put a few photos in your crew quarters.",
                   "Watch Earth from the window and follow when you pass over your home town.",
                   "Celebrate special days together with your crew.",
                   "Share meals and conversations with your crewmates."])},
    {"kod": "stres", "ad": L("Stres ve kaygı", "Stress and anxiety", "Estrés y ansiedad", "Стресс и тревога"),
     "aciklama": L("Yoğun görevler, gürültü ve riskler stresi artırır. Kısa molalar büyük fark yaratır.",
                   "Heavy workload, noise and risks increase stress. Short breaks make a big difference."),
     "adimlar": L(["Her 90 dakikada 5 dakikalık mola ver.",
                   "4-7-8 nefes egzersizini yap.",
                   "Görevlerini küçük adımlara böl ve tek tek tamamla.",
                   "Kaygın 2 günden uzun sürerse mürettebat psikoloğuyla konuş."],
                  ["Take a 5-minute break every 90 minutes.",
                   "Do the 4-7-8 breathing exercise.",
                   "Split tasks into small steps and finish them one by one.",
                   "If anxiety lasts more than 2 days, talk to the crew psychologist."])},
    {"kod": "uyku", "ad": L("Uyku sorunları", "Sleep problems", "Problemas de sueño", "Проблемы со сном"),
     "aciklama": L("Uzayda günde 16 kez gün doğumu görülebilir. Bu, vücudun saatini karıştırır.",
                   "In orbit you may see 16 sunrises a day. This confuses your body clock."),
     "adimlar": L(["Her gün aynı saatte yat ve kalk.",
                   "Uyumadan 1 saat önce ekranları kapat.",
                   "Göz bandı ve kulak tıkacı kullan.",
                   "Uyku kabininin ışığını kırmızı/sıcak renge ayarla."],
                  ["Go to bed and wake up at the same time every day.",
                   "Turn off screens 1 hour before sleep.",
                   "Use an eye mask and earplugs.",
                   "Set your sleep station light to a warm/red tone."])},
    {"kod": "ekip", "ad": L("Ekip içi gerginlik", "Tension in the crew", "Tensión en la tripulación",
                            "Напряжение в экипаже"),
     "aciklama": L("Aylarca aynı kişilerle yaşamak küçük sorunları büyütebilir.",
                   "Living with the same people for months can make small problems feel big."),
     "adimlar": L(["Sorunu büyümeden, sakin bir anda konuş.",
                   "'Sen hep...' yerine 'Ben ... hissediyorum' diye başla.",
                   "Gerekirse komutandan ya da psikologdan arabuluculuk iste.",
                   "Kendine her gün biraz yalnız kalma zamanı ayır."],
                  ["Talk about the issue early, at a calm moment.",
                   "Start with 'I feel...' instead of 'You always...'.",
                   "Ask the commander or psychologist to mediate if needed.",
                   "Give yourself some alone time every day."])},
    {"kod": "motivasyon", "ad": L("Motivasyon kaybı", "Loss of motivation", "Pérdida de motivación",
                                  "Потеря мотивации"),
     "aciklama": L("Görevin ortasında günler birbirine benzemeye başlayabilir. Buna 'üçte bir etkisi' denir.",
                   "Mid-mission, days can start to feel the same. This is known as the 'third-quarter effect'."),
     "adimlar": L(["Kendine küçük hedefler koy ve tamamlayınca kutla.",
                   "Görevinin neden önemli olduğunu hatırla.",
                   "Yeni bir hobi dene: fotoğraf, müzik, çizim.",
                   "Görev puanı ve serini takip et."],
                  ["Set small goals and celebrate when you reach them.",
                   "Remind yourself why your mission matters.",
                   "Try a new hobby: photography, music, drawing.",
                   "Track your task points and streak."])},
]

# ---------------------------------------------------------------
# REGL DÖNGÜSÜ TAKİBİ (kadın profiller)
# Tahminler bilgilendirme amaçlıdır; tıbbi karar için uçuş doktoruna danışılır.
# ---------------------------------------------------------------
VARSAYILAN_DONGU = 28   # gün (geçmişte en az 2 dönem varsa ortalaması kullanılır)
VARSAYILAN_REGL = 5     # gün
DONGU_ARALIGI = (21, 45)

DONGU_EVRELERI = {
    "regl": {"ad": L("Regl", "Period", "Menstruación", "Менструация"), "renk": "#ef4444",
             "ipucu": L("Bol su iç, demir içeren yiyecekler tüket ve yoğun egzersizi hafiflet. Kramp için sıcak "
                        "kompres işe yarar; ağrı kesici gerekiyorsa medikal kontrol listesine ve uçuş doktoruna danış.",
                        "Drink plenty of water, eat iron-rich foods and lighten intense exercise. A warm compress helps "
                        "with cramps; if you need a painkiller, follow the medical checklist and ask the Flight Surgeon.")},
    "folikuler": {"ad": L("Foliküler evre", "Follicular phase", "Fase folicular", "Фолликулярная фаза"),
                  "renk": "#38bdf8",
                  "ipucu": L("Enerjin genellikle artar. Yoğun direnç antrenmanları için iyi bir dönem.",
                             "Energy usually rises. A good time for intense resistance training.")},
    "ovulasyon": {"ad": L("Ovulasyon", "Ovulation", "Ovulación", "Овуляция"), "renk": "#a78bfa",
                  "ipucu": L("Bazı kişilerde hafif kasık ağrısı ve vücut ısısında küçük bir artış olabilir; bu normaldir.",
                             "Some people feel mild pelvic pain and a small rise in body temperature; this is normal.")},
    "luteal": {"ad": L("Luteal evre", "Luteal phase", "Fase lútea", "Лютеиновая фаза"), "renk": "#facc15",
               "ipucu": L("Şişkinlik, yorgunluk ve ruh hali dalgalanmaları görülebilir. Uyku düzenine dikkat et, "
                          "tuzu azalt ve kendine nazik ol.",
                          "Bloating, tiredness and mood swings may appear. Keep a regular sleep routine, reduce salt "
                          "and be kind to yourself.")},
}

REGL_AKIS = {
    "yok": L("Yok", "None", "Ninguno", "Нет"),
    "hafif": L("Hafif", "Light", "Ligero", "Слабые"),
    "orta": L("Orta", "Medium", "Moderado", "Средние"),
    "yogun": L("Yoğun", "Heavy", "Abundante", "Обильные"),
}

REGL_BELIRTILERI = {
    "kramp": L("Kramp", "Cramps", "Calambres", "Спазмы"),
    "bas_agrisi": L("Baş ağrısı", "Headache", "Dolor de cabeza", "Головная боль"),
    "yorgunluk": L("Yorgunluk", "Fatigue", "Fatiga", "Усталость"),
    "siskinlik": L("Şişkinlik", "Bloating", "Hinchazón", "Вздутие"),
    "ruh_hali": L("Ruh hali değişimi", "Mood changes", "Cambios de ánimo", "Перепады настроения"),
    "bel_agrisi": L("Bel ağrısı", "Back pain", "Dolor de espalda", "Боль в спине"),
    "gogus_hassasiyeti": L("Göğüs hassasiyeti", "Breast tenderness", "Sensibilidad mamaria", "Чувствительность груди"),
    "uyku": L("Uyku sorunu", "Sleep problems", "Problemas de sueño", "Проблемы со сном"),
}
