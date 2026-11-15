"""
ASTRA MASAÜSTÜ BAŞLATICISI — ASTRA.exe'nin giriş noktası.

PyInstaller bu dosyayı, Python'u ve bütün paketleri tek bir klasörde paketler.
Böylece Python'u olmayan biri de ASTRA.exe'ye çift tıklayarak uygulamayı açabilir.

- Uygulama dosyaları (main.py, sayfalar, assets...) paketin içinde durur (salt okunur).
- Kullanıcı verileri (veritabanı, ses/video kayıtları) ASTRA.exe'nin yanındaki "ASTRA_veri"
  klasörüne yazılır. Oraya yazılamıyorsa (ör. Program Files) %LOCALAPPDATA%\\ASTRA kullanılır.
"""
import os
import shutil
import sys

# PyInstaller'ın bu paketleri de exe'ye koyması için burada açıkça içe aktarılıyor
# (uygulamanın kendi dosyaları bunları çalışırken kullanıyor).
import sqlite3  # noqa: F401
import io  # noqa: F401
import html  # noqa: F401
import mimetypes  # noqa: F401
import functools  # noqa: F401
import numpy  # noqa: F401
import pandas  # noqa: F401
import plotly.graph_objects  # noqa: F401
import openpyxl  # noqa: F401
from PIL import Image, ImageOps  # noqa: F401
import streamlit.components.v1  # noqa: F401

try:  # isteğe bağlı paketler: yoksa uygulama yine açılır
    import deep_translator  # noqa: F401
    from google import genai  # noqa: F401
    from google.genai import types  # noqa: F401
except ImportError:
    pass


def kaynak_klasoru() -> str:
    """Uygulama dosyalarının bulunduğu yer (exe içinde _MEIPASS, normalde bu dosyanın klasörü)."""
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def veri_klasoru() -> str:
    """Veritabanı ve kayıtların yazılacağı yer."""
    exe_yani = os.path.join(os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False)
                                                          else __file__)), "ASTRA_veri")
    try:
        os.makedirs(exe_yani, exist_ok=True)
        deneme = os.path.join(exe_yani, ".yazma_testi")
        with open(deneme, "w") as f:
            f.write("ok")
        os.remove(deneme)
        return exe_yani
    except OSError:
        yedek = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ASTRA")
        os.makedirs(yedek, exist_ok=True)
        return yedek


def main():
    kaynak = kaynak_klasoru()
    veri = veri_klasoru()

    # Streamlit tema ayarını veri klasörüne kopyala (Streamlit ayarı çalışılan klasörden okur)
    ayar_kaynak = os.path.join(kaynak, ".streamlit", "config.toml")
    if os.path.exists(ayar_kaynak):
        os.makedirs(os.path.join(veri, ".streamlit"), exist_ok=True)
        shutil.copyfile(ayar_kaynak, os.path.join(veri, ".streamlit", "config.toml"))

    os.chdir(veri)                # astronot_saglik.db ve kayitlar/ buraya yazılır
    sys.path.insert(0, kaynak)    # ayarlar.py, arayuz.py ... içe aktarılabilsin

    print("=" * 60)
    print("  ASTRA - Murettebat Saglik Sistemi")
    print("  Uygulama tarayicinizda aciliyor...")
    print("  Kapatmak icin bu pencereyi kapatin.")
    print(f"  Veriler: {veri}")
    print("=" * 60)

    from streamlit.web import cli as stcli
    sys.argv = [
        "streamlit", "run", os.path.join(kaynak, "main.py"),
        "--global.developmentMode=false",
        "--server.headless=false",
        "--server.fileWatcherType=none",
        "--server.runOnSave=false",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
