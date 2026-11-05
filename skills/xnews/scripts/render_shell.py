#!/usr/bin/env python3
"""Render poster HTML -> PNG tanpa browser_exec.

Fallback kalau browser harness mati atau Chrome/Edge sistem crash
("Abnormal renderer termination") di halaman poster.

Pakai Chrome headless shell bawaan Playwright (versi lama, stabil untuk
layout poster), lalu fallback ke Chrome/Edge sistem.

Pemakaian:
    python render_shell.py index.html poster.png [--w 1080] [--h 1350]

Exit code 0 = PNG ada dan ukurannya benar.
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path


def candidates() -> list[str]:
    """Urutan kandidat: playwright headless shell -> chromium playwright -> chrome/edge sistem."""
    out: list[str] = []
    home = Path(os.path.expanduser("~"))
    local = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))

    pw = local / "ms-playwright"
    if pw.is_dir():
        # versi terbaru dulu
        for pat in (
            "chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe",
            "chromium-*/chrome-win64/chrome.exe",
            "chromium_headless_shell-*/chrome-win/chrome-headless-shell.exe",
            "chromium-*/chrome-win/chrome.exe",
        ):
            for p in sorted(glob.glob(str(pw / pat)), reverse=True):
                out.append(p)

    for p in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ):
        if Path(p).is_file():
            out.append(p)
    return out


def run(binary: str, url: str, out: Path, w: int, h: int, timeout: int) -> bool:
    scratch = Path(os.environ.get("TMPDIR") or local_scratch())
    profile = scratch / f"renderprof-{os.getpid()}"
    args = [
        binary,
        "--headless" if "headless-shell" in binary.lower() else "--headless=new",
        "--no-sandbox",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-gpu",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        f"--user-data-dir={profile}",
        f"--window-size={w},{h}",
        f"--screenshot={out}",
        url,
    ]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"  timeout {timeout}s: {Path(binary).name}")
        return False
    ok = out.is_file() and out.stat().st_size > 20_000
    if not ok:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-2:]
        print(f"  gagal: {Path(binary).name} -> {' / '.join(tail) or 'tanpa output'}")
    return ok


def local_scratch() -> str:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    p = base / "hermes" / "cache" / "scratch"
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


def size_of(path: Path) -> tuple[int, int]:
    try:
        from PIL import Image  # type: ignore

        with Image.open(path) as im:
            return im.size
    except Exception:
        return (0, 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("out")
    ap.add_argument("--w", type=int, default=1080)
    ap.add_argument("--h", type=int, default=1350)
    ap.add_argument("--timeout", type=int, default=60)
    a = ap.parse_args()

    html = Path(a.html).resolve()
    out = Path(a.out).resolve()
    if not html.is_file():
        print(f"HTML tidak ada: {html}")
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    url = html.as_uri()
    for binary in candidates():
        print(f"coba: {binary}")
        if run(binary, url, out, a.w, a.h, a.timeout):
            w, h = size_of(out)
            print(f"OK {out} {w}x{h}")
            if (w, h) != (a.w, a.h):
                print(f"  PERINGATAN: ukuran {w}x{h}, harusnya {a.w}x{a.h}")
                return 1
            return 0

    print("SEMUA RENDERER GAGAL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
