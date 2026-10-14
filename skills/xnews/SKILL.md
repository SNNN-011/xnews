---
name: xnews
description: "X/Twitter video -> 9:16 news repost template."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [twitter, x.com, video, 9:16, ffmpeg, news, template, repost]
---

# xnews — X/Twitter video -> template 9:16 news repost

## When to use
User wants to repost X/Twitter video news as 9:16 vertical: original 16:9
video centered-top on black canvas, headline from tweet text, source credit
and render date below video, channel branding (gear-$ logo, M logo, glow).
Repo: `skills/xnews/` — `scripts/xnews.py` (orchestrator),
`scripts/render.py` (template), `scripts/setup.py` (auto-install).

## FIRST RUN: setup otomatis
Pas pertama kali pakai di laptop baru (atau kalau ada error "command not
found" / "No module named"), jalankan setup dulu — dia install semua
requirement otomatis (Pillow, numpy, yt-dlp) dan cek ffmpeg + aset:

```
python scripts/setup.py
```

Setup idempotent — aman diulang. Yang TIDAK otomatis: ffmpeg di Windows
(install via `winget install Gyan.FFmpeg` atau ffmpeg.org), dan Deepgram
API key (opsional, cuma buat fallback transkrip kalau tweet kosong).

## Pipeline
1. `fetch_meta(url)` — yt-dlp `-J`, extractor `twitter` handles x.com.
2. Judul: tweet description (URL stripped, 220 char cap). Kalau <20 char ->
   Deepgram nova-2 transcribe fallback (key: env DEEPGRAM_KEY atau
   ~/.deepgram_key).
3. Duration rule: <=180s single full render; >180s split per segment
   (`--seg 60` default) -> multiple numbered files.
4. Render 1080x1920: video 1025x577 (16:9) at top-middle (VID_LEFT=27,
   VID_TOP=602), headline Poppins REGULAR (auto-shrink 40->26px, max 4
   lines) in zone y 320-565, "SC: X @handle" + dd/mm/yyyy (tanggal RENDER)
   rata kiri di bawah video, gear-$ logo kiri atas, logo M kanan bawah,
   glow kiri bawah.

Pakai: `python scripts/xnews.py <x.com-url> [--seg 60] [--out output/]`
(Python yang punya Pillow+numpy — Hermes venv atau sistem python)

## Layout constants (render.py) — hasil ukur pixel dari template
- VID 1025x577 at (27, 602) — margin kiri-kanan ~28px, video di atas-tengah
- TITLE_ZONE 320-565, Poppins Regular (BUKAN bold — user minta), FONT_STEPS
  [40,36,32,28,26]
- SRC_Y=1215 / DATE_Y=1262, rata KIRI (left_x = VID_LEFT), F_SRC=30 F_DATE=26
- GEAR_BOX=(4,0,212,180), LOGO_M_BOX=(478,1720,490,135)
- Glow: assets_glow.png dari template asli, resize 360x276, posisi kiri bawah

## Customisasi template
- Ganti logo/handle: timpa file di `assets/` (PNG transparan, ukuran bebas —
  render auto-resize ke box di render.py)
- Geser posisi: edit konstanta di render.py (VID_TOP, TITLE_ZONE_*, SRC_Y...)
- Ganti font: taruh TTF baru di assets/, edit `_load()` di render.py

## Pitfalls (verified)
- ffmpeg overlay PNG statis: JANGAN `shortest=1` di overlay kedua — PNG
  1 frame + shortest=1 = output 1 frame. Pakai `[v1][1:v]overlay=0:0` saja.
- Scale video: pakai `scale=w:h:force_original_aspect_ratio=increase` +
  `crop` — BUKAN decrease+pad. Source lebih lebar dari target bikin pad
  error "Padded dimensions cannot be smaller than input dimensions".
- Verifikasi durasi VIDEO STREAM (ffprobe stream=duration,nb_frames), bukan
  format duration — audio bisa 5s walau video stream cuma 1 frame.
- Emoji: Poppins ga punya glyph emoji -> kotak (tofu). render.py switch font
  per karakter ke emoji font OS (Segoe UI Emoji / Noto Color Emoji /
  Apple Color Emoji) dengan `embedded_color=True`. Kalau EMOJI_FONT None
  (Linux tanpa Noto), emoji jadi kotak — install fonts-noto-color-emoji.
- Path di repo portabel: aset relatif ke script dir
  (`SCRIPT_DIR.parent / "assets"`), emoji font auto-detect per-OS.

## Verification
Render testsrc2 5s, ffprobe stream duration harus 5.0s & nb_frames~150,
lalu vision_analyze frame: judul atas (regular) / 16:9 tengah-atas /
sumber+tanggal kiri bawah video / logo gear kiri atas / logo M kanan bawah
/ glow kiri bawah / bg hitam bersih.
