"""
VÜCUT ÇİZİMİ — Röntgen (x-ray) tarzı insan vücudu, iskelet ve organlar (SVG).

- Kadın ve erkek için farklı vücut hatları
- Beyin, akciğerler, kalp, kaslar: durumlarına göre yeşil / sarı / kırmızı
- Vücut kenar çizgisi: vücut ısısının durumu
- Karaciğer, mide, böbrekler, bağırsaklar: görünüm için (ölçüm yok)
- Seçili bölge yavaşça, kırmızı bölge hızlıca yanıp söner
"""
import ayarlar

# Vücudun SAĞ yarısının hat noktaları (x, y). Sol yarı bunun aynası alınarak çizilir.
# Orta çizgi x = 120.
ERKEK_HAT = [
    (120, 6), (134, 9), (143, 20), (146, 36), (144, 52), (139, 64), (132, 74), (131, 82), (133, 90),
    (150, 96), (168, 101), (179, 111), (183, 132), (185, 162), (187, 190), (191, 220), (195, 248),
    (200, 260), (203, 278), (198, 292), (189, 291), (184, 272), (181, 252), (175, 222), (169, 194),
    (165, 162), (161, 134), (159, 152), (157, 178), (153, 206), (158, 234), (162, 260), (162, 292),
    (158, 330), (154, 366), (156, 398), (152, 432), (146, 470), (150, 488), (156, 500), (142, 506),
    (129, 503), (128, 488), (129, 470), (128, 432), (126, 370), (126, 330), (123, 300), (120, 290),
]

KADIN_HAT = [
    (120, 10), (133, 13), (141, 23), (144, 38), (142, 53), (137, 64), (130, 73), (129, 82), (131, 90),
    (146, 97), (161, 103), (170, 113), (174, 134), (176, 162), (178, 190), (182, 220), (186, 247),
    (190, 258), (192, 275), (188, 288), (180, 287), (176, 270), (173, 250), (167, 222), (162, 194),
    (159, 165), (156, 138), (156, 150), (152, 176), (146, 204), (156, 232), (166, 258), (165, 292),
    (159, 330), (153, 366), (155, 398), (150, 432), (144, 470), (148, 488), (153, 499), (140, 504),
    (129, 501), (128, 487), (129, 470), (128, 432), (126, 370), (126, 330), (123, 300), (120, 292),
]


def _yumusak_kapali_yol(noktalar):
    """Noktalardan geçen yumuşak, kapalı bir çizgi (Catmull-Rom eğrisi) oluşturur."""
    n = len(noktalar)
    p = noktalar
    yol = f"M{p[0][0]:.1f},{p[0][1]:.1f} "
    for i in range(n):
        p0, p1, p2, p3 = p[i - 1], p[i], p[(i + 1) % n], p[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        yol += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return yol + "Z"


def _tam_hat(sag_yari):
    sol_yari = [(240 - x, y) for (x, y) in reversed(sag_yari[1:-1])]
    return _yumusak_kapali_yol(sag_yari + sol_yari)


def _ayna(icerik):
    """Bir SVG parçasını hem kendisi hem aynası olarak döndürür."""
    return icerik + f'<g transform="translate(240,0) scale(-1,1)">{icerik}</g>'


def _iskelet(kadin: bool, kemik_rengi: str, bacak_rengi: str):
    k = kemik_rengi
    # omurga
    omurga = "".join(
        f'<rect x="116.5" y="{y}" width="7" height="6" rx="2" fill="{k}" fill-opacity="0.35"/>'
        for y in range(84, 252, 8))
    # kaburgalar (bir taraf, sonra aynası)
    kaburga = ""
    for i in range(8):
        y = 108 + i * 11
        gen = 34 - abs(i - 3) * 2.2 - (2 if kadin else 0)
        kaburga += (f'<path d="M124,{y} Q{124 + gen + 6},{y - 3} {124 + gen},{y + 15}" '
                    f'stroke="{k}" stroke-width="2.2" fill="none" stroke-opacity="0.55"/>')
    leğen_gen = 40 if kadin else 34
    pelvis = (f'<path d="M123,238 Q{123 + leğen_gen},226 {121 + leğen_gen},252 Q{118 + leğen_gen * 0.8},270 '
              f'138,272 L126,282 Z" fill="{k}" fill-opacity="0.18" stroke="{k}" stroke-opacity="0.55" '
              f'stroke-width="1.6"/>')
    omuz_x = 160 if kadin else 166
    kol = (f'<path d="M124,98 Q{omuz_x - 20},96 {omuz_x},104" stroke="{k}" stroke-width="3" fill="none" '
           f'stroke-opacity="0.6"/>'  # köprücük
           f'<line x1="{omuz_x + 6}" y1="112" x2="{omuz_x + 12}" y2="190" stroke="{k}" stroke-width="4" '
           f'stroke-linecap="round" stroke-opacity="0.5"/>'  # üst kol
           f'<line x1="{omuz_x + 12}" y1="194" x2="{omuz_x + 20}" y2="250" stroke="{k}" stroke-width="2.4" '
           f'stroke-linecap="round" stroke-opacity="0.5"/>'
           f'<line x1="{omuz_x + 8}" y1="196" x2="{omuz_x + 15}" y2="252" stroke="{k}" stroke-width="2" '
           f'stroke-linecap="round" stroke-opacity="0.45"/>')
    bacak = (f'<line x1="146" y1="262" x2="141" y2="360" stroke="{bacak_rengi}" stroke-width="5.5" '
             f'stroke-linecap="round" stroke-opacity="0.75"/>'  # uyluk kemiği
             f'<circle cx="141" cy="368" r="5" fill="{bacak_rengi}" fill-opacity="0.55"/>'  # diz kapağı
             f'<line x1="141" y1="378" x2="140" y2="468" stroke="{bacak_rengi}" stroke-width="4.5" '
             f'stroke-linecap="round" stroke-opacity="0.75"/>'
             f'<line x1="147" y1="380" x2="146" y2="466" stroke="{bacak_rengi}" stroke-width="2" '
             f'stroke-linecap="round" stroke-opacity="0.55"/>')
    kafatasi = (f'<ellipse cx="120" cy="38" rx="21" ry="26" fill="none" stroke="{k}" stroke-opacity="0.5" '
                f'stroke-width="1.6"/>'
                f'<path d="M106,56 Q120,72 134,56" fill="none" stroke="{k}" stroke-opacity="0.5" stroke-width="1.6"/>')
    goguskemigi = f'<rect x="117.5" y="104" width="5" height="52" rx="2.5" fill="{k}" fill-opacity="0.35"/>'
    return kafatasi + omurga + goguskemigi + _ayna(kaburga + pelvis + kol + bacak)


def vucut_html(bolge_durumlari: dict, secili_bolge: str, cinsiyet: str = "Kadın",
               etiketler=("NORMAL", "DİKKAT", "ACİL")) -> str:
    kadin = cinsiyet == "Kadın"
    r = {k: ayarlar.RENKLER[v] for k, v in bolge_durumlari.items()}

    def animasyon(bolge):
        if bolge == secili_bolge or bolge_durumlari[bolge] == "kirmizi":
            hiz = "1.4s" if bolge == secili_bolge else "0.8s"
            return (f'<animate attributeName="opacity" values="1;0.4;1" dur="{hiz}" '
                    f'repeatCount="indefinite"/>')
        return ""

    def cerceve(bolge):
        if bolge == secili_bolge:
            return 'stroke="#ffffff" stroke-width="1.8"'
        return 'stroke="#061020" stroke-width="1.2"'

    hat = _tam_hat(KADIN_HAT if kadin else ERKEK_HAT)
    notr = "#7cc4ff"  # ölçüm olmayan organlar

    akciger = ('<path d="M124,104 Q140,100 150,116 Q158,140 155,172 Q142,180 126,172 Z"/>')
    kas = ('<ellipse cx="143" cy="300" rx="13" ry="40"/>'
           '<ellipse cx="144" cy="410" rx="9" ry="30"/>')
    gogus = ('<path d="M128,138 Q144,132 156,146" fill="none" stroke="#9fd4ff" stroke-opacity="0.35" '
             'stroke-width="1.4"/>') if kadin else ""

    return f"""
<div style="position:relative;display:flex;justify-content:center;align-items:center;height:560px;
            background:radial-gradient(ellipse at 50% 40%, #0d2a4a 0%, #050b16 72%);
            border:1px solid #1c2a40;border-radius:6px;overflow:hidden;">
<svg viewBox="0 0 240 520" height="540" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="ten" cx="50%" cy="40%" r="65%">
      <stop offset="0" stop-color="#5fb4ff" stop-opacity="0.38"/>
      <stop offset="1" stop-color="#1e5fa8" stop-opacity="0.16"/>
    </radialGradient>
    <filter id="parilti" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="yumusak"><feGaussianBlur stdDeviation="0.6"/></filter>
  </defs>

  <!-- vücut hattı (kenar rengi = vücut ısısı) -->
  <path d="{hat}" fill="url(#ten)" stroke="{r['genel']}" stroke-width="1.5" stroke-opacity="0.9"
        filter="url(#parilti)">
    <title>{bolge_durumlari['genel']}</title>{animasyon('genel')}
  </path>

  <!-- kaslar (uyluk ve baldır) -->
  <g fill="{r['kaslar']}" fill-opacity="0.32" {cerceve('kaslar') if secili_bolge == 'kaslar' else 'stroke="none"'}>{animasyon('kaslar')}{_ayna(kas)}</g>

  <!-- iskelet -->
  <g filter="url(#yumusak)">{_iskelet(kadin, "#d6ecff", r['kaslar'])}</g>

  <!-- karın organları (görünüm için) -->
  <g fill="{notr}" fill-opacity="0.16" stroke="{notr}" stroke-opacity="0.45" stroke-width="1">
    <path d="M90,178 Q104,170 124,176 Q122,196 104,200 Q92,198 90,178 Z"/>
    <path d="M126,180 Q142,174 150,186 Q150,204 136,206 Q126,200 126,180 Z"/>
    <ellipse cx="103" cy="214" rx="6" ry="10"/><ellipse cx="137" cy="214" rx="6" ry="10"/>
    <rect x="100" y="210" width="40" height="38" rx="14"/>
    <path d="M106,222 Q114,216 120,224 Q126,232 134,224 M106,236 Q114,230 120,238 Q126,244 134,236"
          fill="none"/>
  </g>
  {_ayna(gogus) if gogus else ''}

  <!-- akciğerler -->
  <g fill="{r['akciger']}" fill-opacity="0.55" {cerceve('akciger')} filter="url(#parilti)">
    {animasyon('akciger')}{_ayna(akciger)}
  </g>

  <!-- kalp -->
  <g fill="{r['kalp']}" fill-opacity="0.95" {cerceve('kalp')} filter="url(#parilti)">
    {animasyon('kalp')}
    <path d="M126,140 C126,132 116,130 116,139 C116,147 126,152 128,159
             C130,152 140,147 140,139 C140,130 130,132 128,140 Z"/>
  </g>

  <!-- beyin -->
  <g fill="{r['beyin']}" fill-opacity="0.75" {cerceve('beyin')} filter="url(#parilti)">
    {animasyon('beyin')}
    <path d="M102,32 Q102,15 120,14 Q138,15 138,32 Q138,46 120,46 Q102,46 102,32 Z"/>
  </g>
  <path d="M120,16 L120,44 M110,24 Q115,28 111,34 M130,24 Q125,28 129,34 M107,38 Q112,36 114,40
           M133,38 Q128,36 126,40" stroke="#061020" stroke-width="1" fill="none" opacity="0.55"/>
</svg>
<div style="position:absolute;bottom:10px;left:0;right:0;display:flex;justify-content:center;gap:16px;
            font:600 11px sans-serif;letter-spacing:.08em;color:#8aa0b8;">
  <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;
        margin-right:5px"></span>{etiketler[0]}</span>
  <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#facc15;
        margin-right:5px"></span>{etiketler[1]}</span>
  <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ef4444;
        margin-right:5px"></span>{etiketler[2]}</span>
</div>
</div>
"""


# ---------------------------------------------------------------
# TERMAL VÜCUT — termal kamera görüntüsü gibi (soğuk = mavi, sıcak = kırmızı/beyaz)
# ---------------------------------------------------------------
TERMAL_RENKLER = ["#120a4a", "#2734c9", "#0aa6f5", "#00d68f", "#e6e600", "#ff9100", "#ff2d00", "#fff2e0"]


def termal_renk(v: float) -> str:
    """0 (soğuk) - 1 (sıcak) arası bir değeri termal kamera rengine çevirir."""
    v = min(max(v, 0.0), 1.0) * (len(TERMAL_RENKLER) - 1)
    i = min(int(v), len(TERMAL_RENKLER) - 2)
    oran = v - i
    a, b = TERMAL_RENKLER[i], TERMAL_RENKLER[i + 1]
    kanal = [round(int(a[k:k + 2], 16) * (1 - oran) + int(b[k:k + 2], 16) * oran) for k in (1, 3, 5)]
    return "#" + "".join(f"{c:02x}" for c in kanal)


def termal_html(isi: float, cinsiyet: str, durum: str, baslik: str) -> str:
    kadin = cinsiyet == "Kadın"
    kimlik = "k" if kadin else "e"
    hat = _tam_hat(KADIN_HAT if kadin else ERKEK_HAT)
    kayma = (isi - 36.7) * 0.11  # vücut ısısı yükseldikçe her bölge daha "sıcak" renge kayar

    # (x, y, yatay yarıçap, dikey yarıçap, temel sıcaklık)  — sol taraf; sağ taraf aynası
    bolgeler = [
        (120, 40, 24, 30, 0.74), (120, 84, 12, 10, 0.80),            # baş, boyun
        (120, 140, 34, 42, 0.86), (120, 205, 30, 30, 0.82),          # göğüs, karın
        (103, 255, 16, 20, 0.70),                                     # kasık
        (172, 150, 10, 34, 0.60), (182, 220, 8, 30, 0.48), (196, 275, 8, 14, 0.33),  # kol, önkol, el
        (142, 300, 15, 38, 0.60), (140, 368, 10, 12, 0.46),          # uyluk, diz
        (141, 420, 9, 34, 0.42), (148, 495, 10, 8, 0.26),            # baldır, ayak
    ]
    lekeler = ""
    for x, y, rx, ry, v in bolgeler:
        renk = termal_renk(v + kayma)
        lekeler += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{renk}"/>'
        if x != 120:
            lekeler += f'<ellipse cx="{240 - x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{renk}"/>'
    # en sıcak çekirdek
    lekeler += f'<ellipse cx="120" cy="150" rx="18" ry="30" fill="{termal_renk(0.93 + kayma)}"/>'

    cubuk = "".join(f'<stop offset="{i / (len(TERMAL_RENKLER) - 1):.2f}" stop-color="{c}"/>'
                    for i, c in enumerate(reversed(TERMAL_RENKLER)))
    # renk çubuğunda 33 - 39 °C arası; işaretçi mevcut ısıda
    isaret_y = 40 + (39 - min(max(isi, 33), 39)) / 6 * 420
    renk = ayarlar.RENKLER[durum]
    return f"""
<div style="position:relative;height:560px;background:#03060d;border:1px solid #1c2a40;border-radius:6px;
            overflow:hidden;display:flex;justify-content:center;align-items:center;">
<svg viewBox="0 0 300 520" height="540" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif">
  <defs>
    <clipPath id="govde_{kimlik}"><path d="{hat}"/></clipPath>
    <filter id="bulanik" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
    <linearGradient id="cubuk" x1="0" y1="0" x2="0" y2="1">{cubuk}</linearGradient>
    <pattern id="tarama" width="3" height="3" patternUnits="userSpaceOnUse">
      <rect width="3" height="1" fill="#000" opacity="0.18"/></pattern>
  </defs>
  <g clip-path="url(#govde_{kimlik})">
    <rect width="240" height="520" fill="{termal_renk(0.30 + kayma)}"/>
    <g filter="url(#bulanik)">{lekeler}</g>
    <rect width="240" height="520" fill="url(#tarama)"/>
  </g>
  <path d="{hat}" fill="none" stroke="#ffffff" stroke-opacity="0.18" stroke-width="1"/>
  <!-- renk çubuğu -->
  <rect x="262" y="40" width="10" height="420" rx="3" fill="url(#cubuk)"/>
  <text x="278" y="46" fill="#94a3b8" font-size="9">39°</text>
  <text x="278" y="254" fill="#94a3b8" font-size="9">36°</text>
  <text x="278" y="462" fill="#94a3b8" font-size="9">33°</text>
  <path d="M252,{isaret_y:.0f} l8,-5 v10 z" fill="{renk}"/>
</svg>
<div style="position:absolute;top:14px;left:16px;font:600 11px sans-serif;letter-spacing:.14em;color:#8aa0b8">
  {baslik}</div>
<div style="position:absolute;top:30px;left:16px;font:700 30px sans-serif;color:{renk}">{isi:.1f}°C</div>
</div>
"""


# ---------------------------------------------------------------
# RÖNTGEN VÜCUT HARİTASI — assets/xray_erkek.png fotoğrafı + üstünde organ katmanları
# Kadın için assets/xray_kadin.png eklenirse o kullanılır.
# "Vücut ısısı" seçilince termal renkler fotoğrafın yalnızca vücut kısmına biner
# (fotoğrafın kendisi maske olarak kullanılır, siyah arka plan boyanmaz).
# Koordinatlar 313 x 612 piksellik fotoğrafa göredir.
# ---------------------------------------------------------------
import base64 as _base64
import os as _os

_ASSETS = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets")
_foto_onbellek = {}

# termal katman: (x, y, yatay yarıçap, dikey yarıçap, temel sıcaklık) — orta çizgi x = 157
_TERMAL_BOLGELER = [
    (157, 35, 24, 30, 0.74), (157, 80, 12, 10, 0.80), (157, 150, 40, 48, 0.86), (157, 222, 34, 32, 0.82),
    (157, 282, 30, 20, 0.70), (224, 160, 11, 40, 0.60), (245, 252, 10, 36, 0.48), (275, 322, 15, 24, 0.33),
    (194, 360, 20, 52, 0.60), (196, 436, 13, 12, 0.46), (196, 505, 13, 44, 0.42), (198, 590, 14, 12, 0.26),
]


def _foto(cinsiyet: str):
    dosya = "xray_kadin.png" if cinsiyet == "Kadın" else "xray_erkek.png"
    yol = _os.path.join(_ASSETS, dosya)
    if not _os.path.exists(yol):
        yol = _os.path.join(_ASSETS, "xray_erkek.png")
    if not _os.path.exists(yol):
        return None
    if yol not in _foto_onbellek:
        with open(yol, "rb") as f:
            _foto_onbellek[yol] = _base64.b64encode(f.read()).decode()
    return _foto_onbellek[yol]


def _termal_katman(isi: float) -> str:
    kayma = (isi - 36.7) * 0.11
    lekeler = f'<rect width="313" height="612" fill="{termal_renk(0.30 + kayma)}"/>'
    for x, y, rx, ry, v in _TERMAL_BOLGELER:
        renk = termal_renk(v + kayma)
        lekeler += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{renk}"/>'
        if x != 157:
            lekeler += f'<ellipse cx="{314 - x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{renk}"/>'
    lekeler += f'<ellipse cx="157" cy="160" rx="18" ry="32" fill="{termal_renk(0.93 + kayma)}"/>'
    return f'<g mask="url(#govdeMaskesi)" opacity="0.8"><g filter="url(#termalBulanik)">{lekeler}</g></g>'


def vucut_foto_html(bolge_durumlari: dict, secili_bolge: str, cinsiyet: str = "Erkek",
                    etiketler=("NORMAL", "DİKKAT", "ACİL"), isi: float = None, termal_baslik: str = "",
                    yukseklik: int = 820) -> str:
    foto = _foto(cinsiyet)
    if foto is None:  # fotoğraf yoksa çizim kullanılır
        return vucut_html(bolge_durumlari, secili_bolge, cinsiyet, etiketler)
    r = {k: ayarlar.RENKLER[v] for k, v in bolge_durumlari.items()}

    def animasyon(bolge):
        if bolge == secili_bolge or bolge_durumlari.get(bolge) == "kirmizi":
            hiz = "1.4s" if bolge == secili_bolge else "0.8s"
            return f'<animate attributeName="opacity" values="1;0.35;1" dur="{hiz}" repeatCount="indefinite"/>'
        return ""

    def guc(bolge):
        return 0.75 if bolge == secili_bolge else 0.42

    def cizgi(bolge):
        return 'stroke="#ffffff" stroke-width="1.4" stroke-opacity="0.9"' if bolge == secili_bolge else ""

    termal = secili_bolge == "genel" and isi is not None
    katmanlar = f"""
    <g fill="{r['beyin']}" opacity="{guc('beyin')}">{animasyon('beyin')}
      <ellipse cx="157" cy="26" rx="20" ry="17" filter="url(#yay2)"/>
      <ellipse cx="157" cy="26" rx="20" ry="17" fill="none" {cizgi('beyin')}/></g>
    <g fill="{r['akciger']}" opacity="{guc('akciger')}">{animasyon('akciger')}
      <ellipse cx="131" cy="148" rx="20" ry="40" filter="url(#yay)"/>
      <ellipse cx="184" cy="148" rx="20" ry="40" filter="url(#yay)"/>
      <ellipse cx="131" cy="148" rx="20" ry="40" fill="none" {cizgi('akciger')}/>
      <ellipse cx="184" cy="148" rx="20" ry="40" fill="none" {cizgi('akciger')}/></g>
    <g fill="{r['kalp']}" opacity="{min(1, guc('kalp') + 0.25)}">{animasyon('kalp')}
      <path d="M146,152 C146,145 137,143 137,151 C137,158 146,163 148,169 C150,163 159,158 159,151
               C159,143 150,145 150,152 Z" transform="translate(148,156) scale(1.7) translate(-148,-156)"
            filter="url(#yay2)" {cizgi('kalp')}/></g>
    <g fill="{r['kaslar']}" opacity="{guc('kaslar')}">{animasyon('kaslar')}
      <ellipse cx="121" cy="365" rx="21" ry="58" filter="url(#yay)"/>
      <ellipse cx="194" cy="365" rx="21" ry="58" filter="url(#yay)"/>
      <ellipse cx="118" cy="478" rx="14" ry="42" filter="url(#yay)"/>
      <ellipse cx="196" cy="478" rx="14" ry="42" filter="url(#yay)"/></g>
    """
    if secili_bolge == "radyasyon":
        katmanlar = (f'<rect width="313" height="612" fill="{r["radyasyon"]}" fill-opacity="0.2" '
                     f'mask="url(#govdeMaskesi)"><animate attributeName="fill-opacity" values="0.35;0.08;0.35" '
                     f'dur="1.6s" repeatCount="indefinite"/></rect>') + katmanlar
    if termal:
        katmanlar = _termal_katman(isi)

    ek, yazi = "", ""
    if termal:
        durum_renk = ayarlar.RENKLER[bolge_durumlari["genel"]]
        cubuk = "".join(f'<stop offset="{i / (len(TERMAL_RENKLER) - 1):.2f}" stop-color="{c}"/>'
                        for i, c in enumerate(reversed(TERMAL_RENKLER)))
        isaret_y = 60 + (39 - min(max(isi, 33), 39)) / 6 * 420
        ek = f"""
  <linearGradient id="cubuk" x1="0" y1="0" x2="0" y2="1">{cubuk}</linearGradient>
  <rect x="300" y="60" width="8" height="420" rx="3" fill="url(#cubuk)"/>
  <path d="M290,{isaret_y:.0f} l8,-5 v10 z" fill="{durum_renk}"/>
  <text x="311" y="64" fill="#94a3b8" font-size="9" font-family="sans-serif">39°</text>
  <text x="311" y="274" fill="#94a3b8" font-size="9" font-family="sans-serif">36°</text>
  <text x="311" y="484" fill="#94a3b8" font-size="9" font-family="sans-serif">33°</text>"""
        yazi = (f'<div style="position:absolute;top:16px;left:18px;font:600 11px sans-serif;letter-spacing:.14em;'
                f'color:#8aa0b8">{termal_baslik}</div>'
                f'<div style="position:absolute;top:32px;left:18px;font:700 32px sans-serif;color:{durum_renk}">'
                f'{isi:.1f}°C</div>')

    svg_yukseklik = yukseklik - 40
    return f"""
<style>html,body{{margin:0;padding:0;overflow:hidden}}</style>
<div style="position:relative;display:flex;justify-content:center;align-items:center;height:{yukseklik}px;
            background:#000;border:1px solid #1c2a40;border-radius:6px;overflow:hidden;box-sizing:border-box">
<svg viewBox="0 0 313 612" height="{svg_yukseklik}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
  <defs>
    <filter id="yay" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="7"/></filter>
    <filter id="yay2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2"/></filter>
    <filter id="termalBulanik" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
    <filter id="parlat"><feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer><feFuncR type="linear" slope="5"/><feFuncG type="linear" slope="5"/>
      <feFuncB type="linear" slope="5"/></feComponentTransfer></filter>
    <mask id="govdeMaskesi" maskUnits="userSpaceOnUse" x="0" y="0" width="313" height="612">
      <image href="data:image/png;base64,{foto}" width="313" height="612" filter="url(#parlat)"/></mask>
  </defs>
  <image href="data:image/png;base64,{foto}" x="0" y="0" width="313" height="612"/>
  {katmanlar}{ek}
</svg>
{yazi}
<div style="position:absolute;bottom:12px;left:0;right:0;display:flex;justify-content:center;gap:16px;
            font:600 11px sans-serif;letter-spacing:.08em;color:#8aa0b8;">
  <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;
        margin-right:5px"></span>{etiketler[0]}</span>
  <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#facc15;
        margin-right:5px"></span>{etiketler[1]}</span>
  <span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ef4444;
        margin-right:5px"></span>{etiketler[2]}</span>
</div>
</div>
"""
