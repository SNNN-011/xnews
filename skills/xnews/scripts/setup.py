#!/usr/bin/env python3
"""Auto-setup xnews: cek & install semua requirement.

Dijalankan otomatis pas skill xnews dipakai pertama kali. Aman dijalankan
berulang (idempotent) — yang sudah ada akan di-skip.

Yang dipasang:
  - Python packages: pillow, numpy
  - yt-dlp (download video dari x.com)
  - ffmpeg (render video)
  - (opsional) Deepgram API key buat fallback transkrip

Pakai: python setup.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REQUIREMENTS = ["pillow>=10.0", "numpy>=1.24"]


def _ok(msg):
    print(f"  [OK] {msg}")


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def check_python_packages() -> bool:
    print("Cek Python packages...")
    r = _run([sys.executable, "-m", "pip", "install", "--quiet"] + REQUIREMENTS)
    if r.returncode != 0:
        print(f"  [GAGAL] pip install: {r.stderr.strip()[-300:]}")
        return False
    _ok("pillow + numpy terpasang")
    return True


def check_yt_dlp() -> bool:
    print("Cek yt-dlp...")
    if shutil.which("yt-dlp"):
        _ok("yt-dlp sudah ada")
        return True
    r = _run([sys.executable, "-m", "pip", "install", "--quiet", "yt-dlp"])
    if r.returncode == 0:
        _ok("yt-dlp terpasang via pip")
        return True
    print("  [GAGAL] install yt-dlp — install manual: pip install yt-dlp")
    return False


def check_ffmpeg() -> bool:
    print("Cek ffmpeg...")
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        _ok("ffmpeg sudah ada")
        return True
    system = sys.platform
    if system == "win32":
        print("  [!] ffmpeg tidak ditemukan. Install salah satu cara:")
        print("      - winget install Gyan.FFmpeg")
        print("      - choco install ffmpeg")
        print("      - download dari https://ffmpeg.org/download.html")
        print("        lalu tambahkan ke PATH")
    elif system == "darwin":
        print("  [!] ffmpeg tidak ditemukan. Install: brew install ffmpeg")
    else:
        print("  [!] ffmpeg tidak ditemukan. Install: sudo apt install ffmpeg")
    return False


def check_assets() -> bool:
    print("Cek aset template (logo, font)...")
    assets = SKILL_DIR / "assets"
    needed = ["Poppins-Bold.ttf", "Poppins-Regular.ttf",
              "assets_gear.png", "assets_logoM.png", "assets_glow.png"]
    missing = [f for f in needed if not (assets / f).exists()]
    if missing:
        print(f"  [GAGAL] aset hilang: {missing}")
        print("         Clone ulang repo — folder assets/ harus lengkap")
        return False
    _ok(f"semua {len(needed)} aset ada")
    return True


def check_deepgram() -> bool:
    print("Cek Deepgram key (opsional, buat fallback transkrip)...")
    import os
    if os.environ.get("DEEPGRAM_KEY"):
        _ok("DEEPGRAM_KEY ada di env")
        return True
    if (Path.home() / ".deepgram_key").exists():
        _ok("~/.deepgram_key ada")
        return True
    print("  [!] Deepgram key belum diset (opsional)")
    print("      Kalau tweet kosong, judul diambil dari transkrip audio.")
    print("      Set env DEEPGRAM_KEY atau taruh key di ~/.deepgram_key")
    print("      Daftar gratis: https://deepgram.com")
    return True  # opsional, bukan blocker


def main():
    print("=== xnews setup ===\n")
    results = {
        "python packages": check_python_packages(),
        "yt-dlp": check_yt_dlp(),
        "ffmpeg": check_ffmpeg(),
        "aset template": check_assets(),
        "deepgram": check_deepgram(),
    }
    print("\n=== Ringkasan ===")
    all_ok = True
    for name, ok in results.items():
        status = "OK" if ok else "PERLU DIINSTALL"
        print(f"  {name}: {status}")
        if name != "deepgram" and not ok:
            all_ok = False
    print()
    if all_ok:
        print("Siap pakai! Jalankan:")
        print("  python scripts/xnews.py <url-x.com>")
    else:
        print("Masih ada yang perlu diinstall manual — lihat instruksi di atas.")
        sys.exit(1)


if __name__ == "__main__":
    main()
