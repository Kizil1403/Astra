"""
RÖNTGEN (X-RAY) ÇİZİMİ — Fotoğraf kullanmadan, tamamen kodla çizilen vücut ve iskelet.

Koordinatlar 313 x 612'lik bir alana göredir (orta çizgi x = 157).
- xray_govde(): saydam mavi vücut + parlayan iskelet
- XRAY_HAT: vücudun dış hattı (termal katmanı vücuda kırpmak için de kullanılır)
"""

ORTA = 157

# Vücudun SAĞ yarısının dış hattı (baştan aşağı, kol dışı -> el -> kol içi -> gövde -> bacak -> kasık)
SAG_YARI = [
    (157, 7), (170, 10), (179, 20), (183, 35), (181, 50), (176, 61), (170, 71), (171, 82), (186, 90),
    (204, 97), (217, 104), (227, 116), (232, 140), (235, 172), (239, 204), (248, 238), (258, 268),
    (266, 289), (279, 303), (291, 320), (290, 338), (282, 349), (272, 344), (263, 330), (256, 313),
    (249, 298), (239, 270), (228, 240), (220, 210), (213, 178), (207, 150), (204, 176), (202, 206),
    (203, 232), (209, 258), (213, 288), (212, 322), (208, 360), (204, 405), (206, 438), (208, 478),
    (202, 528), (197, 563), (205, 585), (207, 600), (189, 605), (178, 598), (177, 566), (176, 522),
    (174, 474), (172, 432), (169, 390), (166, 345), (162, 318), (157, 310),
]


def _yumusak_yol(noktalar):
    n = len(noktalar)
    p = noktalar
    yol = f"M{p[0][0]:.1f},{p[0][1]:.1f} "
    for i in range(n):
        p0, p1, p2, p3 = p[i - 1], p[i], p[(i + 1) % n], p[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        yol += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return yol + "Z"


def _ayna_nokta(x, y):
    return 2 * ORTA - x, y


def _kadin_hatti(noktalar):
    """Erkek hattından kadın hattı: omuzlar daha dar, bel daha ince, kalça daha geniş."""
    sonuc = []
    for x, y in noktalar:
        if x == ORTA:
            sonuc.append((x, y))
            continue
        if 88 <= y <= 150:
            dx = -9
        elif 150 < y <= 300 and x > 230:  # kollar omuzla birlikte içeri
            dx = -9
        elif 190 <= y <= 220:
            dx = -6
        elif 235 <= y <= 330:
            dx = 6
        else:
            dx = 0
        sonuc.append((x + dx, y))
    return sonuc


def hat(kadin: bool = False) -> str:
    sag = _kadin_hatti(SAG_YARI) if kadin else SAG_YARI
    return _yumusak_yol(sag + [_ayna_nokta(x, y) for (x, y) in reversed(sag[1:-1])])


XRAY_HAT = hat(False)


def _ayna(icerik: str) -> str:
    return icerik + f'<g transform="translate({2 * ORTA},0) scale(-1,1)">{icerik}</g>'


def _kemik(x1, y1, x2, y2, kalinlik, uc=1.6):
    """Uçları kalın (eklem başlı) uzun kemik."""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="url(#kemik)" stroke-width="{kalinlik}" '
            f'stroke-linecap="round"/>'
            f'<circle cx="{x1}" cy="{y1}" r="{kalinlik * uc / 2}" fill="url(#kemikDolgu)"/>'
            f'<circle cx="{x2}" cy="{y2}" r="{kalinlik * uc / 2}" fill="url(#kemikDolgu)"/>')


def _iskelet() -> str:
    # --- kafatası ---
    kafa = ('<ellipse cx="157" cy="33" rx="21" ry="25" fill="url(#kemikDolgu)" fill-opacity="0.38" '
            'stroke="#d8f0ff" stroke-width="1.4"/>'
            '<ellipse cx="149" cy="40" rx="4.5" ry="3.6" fill="#0a1a2c" opacity="0.45"/>'
            '<ellipse cx="165" cy="40" rx="4.5" ry="3.6" fill="#0a1a2c" opacity="0.45"/>'
            '<path d="M154,47 L157,52 L160,47" fill="none" stroke="#06101d" stroke-width="1.4" opacity="0.7"/>'
            '<path d="M142,52 Q144,66 157,70 Q170,66 172,52" fill="url(#kemikDolgu)" fill-opacity="0.5" '
            'stroke="#d8f0ff" stroke-width="1.3"/>'
            '<path d="M148,58 H166" stroke="#06101d" stroke-width="1.2" opacity="0.6"/>')
    # --- omurga (boyun -> kuyruk sokumu) ---
    omurga = "".join(
        f'<rect x="{157 - w / 2:.1f}" y="{y}" width="{w:.1f}" height="6.2" rx="2" fill="url(#kemikDolgu)"/>'
        for y, w in [(y, 7 + min(4, (y - 74) / 40)) for y in range(74, 252, 8)])
    sakrum = '<path d="M150,252 L164,252 L161,282 L157,290 L153,282 Z" fill="url(#kemikDolgu)" opacity="0.9"/>'
    # --- köprücük kemiği, kürek kemiği ---
    omuz = ('<path d="M162,98 Q184,94 208,104" fill="none" stroke="url(#kemik)" stroke-width="3.4" '
            'stroke-linecap="round"/>'
            '<path d="M186,104 Q206,108 204,140 Q192,146 184,128 Z" fill="url(#kemikDolgu)" fill-opacity="0.35" '
            'stroke="#cfe9ff" stroke-width="1" stroke-opacity="0.6"/>')
    # --- kaburgalar ---
    kaburga = ""
    for i in range(10):
        y = 104 + i * 10.5
        gen = 42 - abs(i - 4) * 2.6 - (4 if i > 7 else 0)
        kaburga += (f'<path d="M161,{y:.1f} C{161 + gen * 0.7:.1f},{y - 6:.1f} {161 + gen:.1f},{y + 2:.1f} '
                    f'{161 + gen - 2:.1f},{y + 16:.1f} C{161 + gen - 6:.1f},{y + 22:.1f} '
                    f'{161 + gen * 0.55:.1f},{y + 18:.1f} {161 + gen * 0.42:.1f},{y + 15:.1f}" '
                    f'fill="none" stroke="url(#kemik)" stroke-width="2.3" stroke-linecap="round" opacity="0.9"/>')
    gogus = '<rect x="154" y="102" width="6" height="56" rx="3" fill="url(#kemikDolgu)" opacity="0.8"/>'
    # --- leğen kemiği ---
    pelvis = ('<path d="M163,248 C176,238 196,240 198,256 C199,268 190,276 182,280 C177,290 169,297 160,299 '
              'L160,288 C167,283 170,272 165,262 Z" fill="url(#kemikDolgu)" fill-opacity="0.42" '
              'stroke="#d8f0ff" stroke-width="1.3"/>'
              '<path d="M172,256 C182,250 190,254 189,262" fill="none" stroke="#d8f0ff" stroke-width="1" opacity="0.6"/>'
              '<circle cx="184" cy="287" r="6.5" fill="url(#kemikDolgu)"/>'
              '<ellipse cx="171" cy="291" rx="5" ry="4.5" fill="#0a1a2c" opacity="0.5"/>')
    # --- kol: üst kol, ön kol (2 kemik), el ---
    kol = (_kemik(212, 112, 226, 206, 6) + _kemik(228, 214, 258, 290, 3.6) + _kemik(222, 216, 251, 294, 3))
    el = "".join(f'<path d="M{258 + i * 2},{298 + i * 1.5} L{266 + i * 6},{322 + i * 2} L{268 + i * 7},{340 + i}" '
                 f'fill="none" stroke="url(#kemik)" stroke-width="1.7" stroke-linecap="round"/>' for i in range(4))
    el += '<path d="M256,300 L262,316 L264,328" fill="none" stroke="url(#kemik)" stroke-width="1.7" stroke-linecap="round"/>'
    # --- bacak: uyluk, diz kapağı, kaval + kamış kemiği, ayak ---
    bacak = (_kemik(186, 292, 192, 424, 7.5, 1.5)
             + '<circle cx="193" cy="436" r="6" fill="url(#kemikDolgu)"/>'
             + _kemik(192, 446, 190, 566, 6, 1.4) + _kemik(201, 450, 198, 560, 2.6, 1.6)
             + '<path d="M184,572 Q194,566 200,576 L206,598 Q196,604 184,600 Z" fill="url(#kemikDolgu)" '
               'fill-opacity="0.85"/>')
    return kafa + omurga + sakrum + gogus + _ayna(omuz + kaburga + pelvis + kol + el + bacak)


def xray_govde(kadin: bool = False) -> str:
    """SVG içine konacak röntgen vücut parçası (defs dahil)."""
    XRAY_HAT = hat(kadin)
    return f"""
  <defs>
    <linearGradient id="kemik" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#f4fbff"/><stop offset="1" stop-color="#8fc8f0"/></linearGradient>
    <radialGradient id="kemikDolgu" cx="40%" cy="35%" r="70%">
      <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#b9e0fb"/>
      <stop offset="1" stop-color="#5d9fd0"/></radialGradient>
    <radialGradient id="ten" cx="50%" cy="38%" r="70%">
      <stop offset="0" stop-color="#1d3f60" stop-opacity="0.55"/>
      <stop offset="0.75" stop-color="#112a44" stop-opacity="0.5"/>
      <stop offset="1" stop-color="#2a5d8a" stop-opacity="0.55"/></radialGradient>
    <filter id="kenarIsigi" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="kemikIsigi" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="xrayGovde"><path d="{XRAY_HAT}"/></clipPath>
  </defs>
  <path d="{XRAY_HAT}" fill="url(#ten)"/>
  <path d="{XRAY_HAT}" fill="none" stroke="#6fb3e6" stroke-width="1.8" stroke-opacity="0.75"
        filter="url(#kenarIsigi)"/>
  <path d="{XRAY_HAT}" fill="none" stroke="#d6eeff" stroke-width="0.6" stroke-opacity="0.5"/>
  <g filter="url(#kemikIsigi)" opacity="0.95">{_iskelet()}</g>
"""
