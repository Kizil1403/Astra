"""
CANLI NABIZ MONİTÖRÜ — Hastane monitörü gibi sürekli akan EKG ve oksijen (pleth) dalgası.

Dalga tarayıcıda (JavaScript) çizilir; bu yüzden sayfa yenilenmeden sürekli hareket eder.
Hızı son ölçülen nabza göre ayarlanır.
"""


def nabiz_monitoru_html(nabiz: float, spo2: float, nabiz_rengi: str, spo2_rengi: str,
                        etiketler: dict) -> str:
    nabiz = max(30, min(200, float(nabiz)))
    return f"""
<style>html,body{{margin:0;padding:0;overflow:hidden}}</style>
<div style="display:flex;height:150px;background:#050b16;border:1px solid #1c2a40;border-radius:6px;
            overflow:hidden;font-family:sans-serif">
  <div style="width:215px;padding:14px 18px;border-right:1px solid #1c2a40;display:flex;flex-direction:column;
              justify-content:space-between">
    <div style="font-size:10px;letter-spacing:.16em;color:#8aa0b8;font-weight:600">{etiketler['baslik']}</div>
    <div style="display:flex;align-items:center;gap:10px">
      <svg id="kalp" width="26" height="26" viewBox="0 0 24 24" fill="{nabiz_rengi}"
           style="filter:drop-shadow(0 0 6px {nabiz_rengi})">
        <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2
                 A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
      <div><span style="font-size:42px;font-weight:800;color:{nabiz_rengi};line-height:1">{nabiz:.0f}</span>
           <span style="font-size:12px;color:#8aa0b8"> bpm</span></div>
    </div>
    <div style="font-size:12px;color:#8aa0b8">SpO2 <b style="color:{spo2_rengi};font-size:16px">{spo2:.0f}%</b>
         &nbsp;·&nbsp; {etiketler['sonraki']}</div>
  </div>
  <div style="flex:1;position:relative;
       background-image:linear-gradient(#0f1d33 1px,transparent 1px),linear-gradient(90deg,#0f1d33 1px,transparent 1px);
       background-size:22px 22px">
    <canvas id="c" style="width:100%;height:100%;display:block"></canvas>
    <div style="position:absolute;top:8px;left:12px;font-size:10px;letter-spacing:.14em;color:{nabiz_rengi}">II · EKG</div>
    <div style="position:absolute;top:92px;left:12px;font-size:10px;letter-spacing:.14em;color:{spo2_rengi}">PLETH · SpO2</div>
  </div>
</div>
<style>
  @keyframes atis {{ 0%,100% {{transform:scale(1)}} 12% {{transform:scale(1.25)}} 30% {{transform:scale(1)}} }}
  #kalp {{ animation: atis {60 / nabiz:.3f}s infinite; transform-origin:center; }}
</style>
<script>
const c = document.getElementById('c'), g = c.getContext('2d');
let G, Y;
function boyutla() {{
  if (G === c.clientWidth && Y === c.clientHeight) return;   // boyut değişmediyse çizimi silme
  const o = window.devicePixelRatio || 1;
  c.width = c.clientWidth * o; c.height = c.clientHeight * o;
  g.setTransform(o, 0, 0, o, 0, 0); G = c.clientWidth; Y = c.clientHeight;
}}
boyutla(); window.addEventListener('resize', boyutla);

const NABIZ = {nabiz:.1f}, HIZ = 110;            // piksel / saniye
let periyot = 60 / NABIZ, faz = 0, x = 0, onceki = null, son = null;

function tepe(f, m, h, w) {{ return h * Math.exp(-((f - m) ** 2) / (2 * w * w)); }}
function ekg(f) {{
  return tepe(f, .18, .12, .025) + tepe(f, .36, -.12, .008) + tepe(f, .39, 1, .011)
       + tepe(f, .42, -.25, .011) + tepe(f, .65, .30, .045);
}}
function pleth(f) {{
  const k = (f + .82) % 1;
  return tepe(k, .22, 1, .07) + tepe(k, .48, .35, .06);
}}

function kare(zaman) {{
  if (son === null) son = zaman;
  let dt = Math.min(.05, (zaman - son) / 1000); son = zaman;
  const adimlar = 4;
  for (let i = 0; i < adimlar; i++) {{
    const d = dt / adimlar;
    faz += d / periyot;
    if (faz >= 1) {{ faz -= 1; periyot = (60 / NABIZ) * (0.96 + Math.random() * 0.08); }}
    const yeniX = x + HIZ * d;
    const y1 = Y * 0.46 - ekg(faz) * Y * 0.36 + (Math.random() - .5) * 1.2;
    const y2 = Y * 0.93 - pleth(faz) * Y * 0.24;
    if (onceki) {{
      g.lineWidth = 2; g.lineCap = 'round';
      g.shadowBlur = 8;
      g.strokeStyle = '{nabiz_rengi}'; g.shadowColor = '{nabiz_rengi}';
      g.beginPath(); g.moveTo(onceki[0], onceki[1]); g.lineTo(yeniX, y1); g.stroke();
      g.strokeStyle = '{spo2_rengi}'; g.shadowColor = '{spo2_rengi}'; g.lineWidth = 1.6;
      g.beginPath(); g.moveTo(onceki[0], onceki[2]); g.lineTo(yeniX, y2); g.stroke();
    }}
    g.clearRect(yeniX + 1, 0, 26, Y);                 // önündeki eski çizgiyi sil (tarama efekti)
    onceki = [yeniX, y1, y2]; x = yeniX;
    if (x > G) {{ x = 0; onceki = null; g.clearRect(0, 0, 28, Y); }}
  }}
  requestAnimationFrame(kare);
}}
requestAnimationFrame(kare);
</script>
"""
