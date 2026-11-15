<p align="center"><img src="assets/logo.png" width="120" alt="ASTRA logo"></p>

<h1 align="center">ASTRA — Crew Health Monitoring System</h1>
<p align="center"><b>NASA Space Apps Challenge · Create Health Monitoring Software for Astronauts on Space Missions</b></p>

---

## English

**ASTRA** is a health monitoring and support system for astronauts on the ISS, lunar and Mars bases, rovers and
deep-space transit. Astronauts are not doctors, so ASTRA explains every value in plain language and tells them
exactly what to do — and when to contact the Flight Surgeon.

### Features
- **Live vitals** from a (simulated) smartwatch every 3 minutes: heart rate, blood oxygen, respiration, body
  temperature, HRV stress indicator, sleep and exercise — each with its normal range and color status.
- **Animated live ECG / pleth monitor** and an **interactive X-ray body map** (brain, lungs, heart, muscles) with a
  **thermal view** and **cumulative radiation** tracking against NASA's 600 mSv career limit.
- **Charts**: hourly averages, warning/critical threshold lines, Excel and CSV export.
- **Safety and Support**: daily mood check-in, personal plan, guided breathing, guides for homesickness, stress,
  sleep and crew conflict, one-tap support requests, and **menstrual cycle tracking** for female astronauts.
- **Journal** with text, voice and video entries; search and sort.
- **Polaris**, the onboard AI assistant (Google Gemini), which receives all current ASTRA values as context and can
  read attached audio, video, documents and images.
- **Gamified daily tasks**: water tracker, 90-minute workout timer, breathing exercise, points, levels and streaks.
- 14 languages, notifications, profile photo, mission environments (ISS, Moon, Mars, deep space, rover).

### Run locally
```bash
pip install -r requirements.txt
streamlit run main.py
```
On Windows you can simply double-click `ASTRA_baslat.bat`. `exe_olustur.bat` builds a standalone `ASTRA.exe`
that runs without Python.

### Deploy on Streamlit Community Cloud
Main file: `main.py`. In **Advanced settings → Secrets** add:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
bulut_modu = true
```
`bulut_modu` gives every visitor their own private database (their ID is kept in the page address).

> Watch data is simulated for the hackathon. Normal ranges are example values. ASTRA does not replace a doctor.

---

## Türkçe

**ASTRA**, ISS, Ay ve Mars üsleri, keşif araçları ve derin uzay yolculuklarındaki astronotlar için bir sağlık
izleme ve destek sistemidir. Astronotlar doktor değildir; bu yüzden ASTRA her değeri sade bir dille açıklar, ne
yapılması gerektiğini ve ne zaman uçuş doktoruna haber verileceğini söyler.

**Öne çıkanlar:** canlı saat verileri ve renkli durumlar, hareketli EKG, röntgen vücut haritası ve termal görünüm,
radyasyon takibi, saatlik grafikler ve Excel/CSV indirme, ruh sağlığı desteği ve aile/Dünya özlemi bölümü, kadın
astronotlar için regl döngüsü takibi, yazı/ses/video günlüğü, Gemini tabanlı yapay zeka Polaris, oyunlaştırılmış
günlük görevler ve 14 dil desteği.

**Çalıştırmak için:** `pip install -r requirements.txt` ve `streamlit run main.py`
(Windows'ta `ASTRA_baslat.bat` dosyasına çift tıklamak yeterli).
