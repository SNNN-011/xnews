---
name: xnews
description: "News link or X video to 9:16 reels or 4:5 poster."
version: 3.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [twitter, x.com, video, 9:16, poster, 4:5, instagram, ffmpeg, news, template]
---

# xnews — berita dari X/link -> video reels 9:16 atau poster 4:5

## When to use
Dua bentuk output dari satu skill ini:

- **video reels 9:16** — repost video berita X/Twitter: video 16:9 di atas-tengah,
  judul dari teks tweet, kredit sumber + tanggal, branding channel.
- **poster 4:5** — kartu berita dari X post, blog, web, atau artikel: foto + headline
  besar di kanvas 1080x1350.

Dua-duanya WAJIB keluar bareng **caption IG** (gaya m4cro.news) — bukan opsional.
Repo: `skills/xnews/` — `scripts/xnews.py` (orchestrator video),
`scripts/render.py` (template video), `scripts/setup.py` (auto-install),
`templates/poster-4x5.html` (template poster), `scripts/grade_photo.py`,
`scripts/fetch_commons.py`, `scripts/poster_checks.js`.

## LANGKAH 0 — tanya bentuknya dulu
Kalau user BELUM menyebut bentuk output, tanya dulu SATU pertanyaan:

> "Mau dibikin poster (gambar 4:5) atau video reels (9:16)?"

- jawab **poster** -> kerjakan `## Pipeline POSTER (4:5)`
- jawab **video / reels / repost video** -> kerjakan `## Pipeline`

Kalau user sudah menyebut sendiri ("bikinin poster", "jadiin reels"), jangan tanya
lagi, langsung ke pipeline-nya. Jangan pernah render dua-duanya tanpa diminta.

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
3. Judul: teks tweet apa adanya. **Agent (Hermes) yang translate ke
   Bahasa Indonesia pakai LLM-nya sendiri**, lalu render ulang pakai
   `--title "<judul ID>"`. Script xnews.py TIDAK manggil LLM apa pun —
   semua kerja LLM (translate, research, caption) dikerjain agent.
   **Watermark (WM):** agent WAJIB lihat frame video (vision) buat cari WM
   sumber asli (video repost YouTube biasanya ada). Kalau ketemu, render
   pakai `--wmsrc "<nama sumber di WM>"` biar masuk baris SC. Script tidak
   bisa baca WM sendiri.
4. Duration rule: <=180s single full render; >180s split per segment
   (`--seg 60` default) -> multiple numbered files.
5. Render 1080x1920: video 1025x577 (16:9) at top-middle (VID_LEFT=27,
   VID_TOP=602), headline Poppins REGULAR (auto-shrink 34->22px, max 4
   lines) in zone y 320-565, baris sumber + dd/mm/yyyy (tanggal RENDER)
   rata kiri di bawah video. Judul auto Title Case (tiap kata huruf
   pertama kapital, termasuk kata sambung).
   Format sumber (build_src_line), wmsrc = nama sumber watermark asli:
   - X/Twitter + WM: "SC: <wm> X@handle" — tanpa kutip
   - X/Twitter tanpa WM: "SC: X@handle" — TANPA spasi setelah X, pakai
     handle asli (uploader_id, bukan nama display — Exilenova_plus bukan
     Exilenova+)
   - YouTube/sumber lain + WM: "SC: <wm>" (WM = nama channel sumber)
   - YouTube/sumber lain tanpa WM: "SC: Nama Channel" — tanpa prefix X
   rata kiri di bawah video, "TikTok: m4croNews" / "IG: m4croNews" rata
   tengah bawah (SEKALI saja), gear-$ logo kiri atas, logo M bersih kanan
   bawah, glow kiri bawah.

Pakai: `python scripts/xnews.py <x.com-url> [--seg 60] [--out output/] [--title "..."] [--wmsrc "CNN"]`
(Python yang punya Pillow+numpy — Hermes venv atau sistem python)

## Pipeline POSTER (4:5) — dari link mana pun
Input boleh X post, blog, web, atau artikel. Output: `poster.png` 1080x1350 + caption IG.

1. **Baca sumbernya.** `web_extract` untuk blog/artikel/web. Untuk X: `web_search`
   cerita yang sama dan/atau baca DOM lewat browser Hermes (`browser_exec`, `new_tab` +
   `js`). Simpan URL asli buat kredit.
2. **Tulis copy dulu, sebelum pixel.** Headline 3-4 baris pendek, UPPERCASE, maksimal
   ~15 karakter per baris di 86px (`--headline-measure: 880px`). Baris terakhir = kata
   aksen. Jangan mengarang angka, nama, atau kutipan.
3. **Ambil gambar dari link dulu.** Cek semua `img src`, `og:image`, `twitter:image`.
   Verifikasi sebelum dipakai: HTTP 200, byte wajar, magic number gambar asli, lebar
   >= 1200px. Kalau link TIDAK punya gambar yang layak:
   `python scripts/fetch_commons.py "<subjek>"` lalu `--get <n>` (Wikimedia Commons,
   cetak judul + lisensi buat kredit). Jangan pakai placeholder.
4. **Grade fotonya** (baked, bukan CSS filter):
   `python scripts/grade_photo.py <foto-raw> <project>/assets/photo-graded.png`
5. **Bangun halaman.** Copy `templates/poster-4x5.html` -> `<project>/index.html`, lalu
   copy `assets/logoM.png`, `assets/gear.png`, `assets/glow.png`,
   `assets/montserrat-400.woff2`, `assets/montserrat-800.woff2` ke `<project>/assets/`.
   Ganti 4 `<span class="ln">`, teks handle, dan `--accent`. Detail angka:
   `references/poster-layout.md`.
6. **Render + asersi + ekspor** lewat `browser_exec`: set viewport 1080x1350
   (`Emulation.setDeviceMetricsOverride`), reload, tunggu `document.fonts.ready` +
   semua `img.complete`, jalankan `scripts/poster_checks.js` via `js(...)`, lalu
   `Page.captureScreenshot` -> `poster.png`.
7. **Caption IG** pakai `references/caption-research.md` (spesifikasi sama dengan video),
   lalu kirim `MEDIA:<poster.png>` + caption + tabel angka hasil ukur.

## Layout constants (render.py) — hasil ukur pixel dari template
- VID 1025x577 at (27, 602) — margin kiri-kanan ~28px, video di atas-tengah
- Layout LANDSCAPE: TITLE_ZONE 400-600, video slot 1025x577 at (27,602)
- Layout PORTRAIT: video slot besar 900x1240 at (0,380) — video 2x lebih besar;
  TITLE_ZONE 100-360, SC+ tanggal rata TENGAH di y 1650-1696, handle tetap 1770
- Video portrait: blur-fill (blur bg 1080x1240 + foreground utuh fit box),
  landscape: scale+crop penuh slot (BUKAN bold — user minta), FONT_STEPS
  [34,30,27,24,22]
- SRC_Y=1215 / DATE_Y=1262, rata KIRI (left_x = VID_LEFT), F_SRC=30 F_DATE=26
- Format sumber: X -> "SC: X@handle" (tanpa spasi, uploader_id);
  YouTube -> "SC: Nama Channel" (uploader). Kalau ada WM (--wmsrc):
  X -> "SC: <wm> X@handle", YouTube -> "SC: <wm>".
- Judul: Title Case otomatis (tiap kata huruf pertama kapital, termasuk
  kata sambung) — berlaku untuk tweet asli maupun --title
- HANDLE_Y=1770 / HANDLE_LINE_H=50, F_HANDLE=34, Poppins regular, rata tengah
- GEAR_BOX=(4,0,212,180), LOGO_M_BOX=(870,1720,95,95)
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
- Ekstrak aset dari screenshot template: CEK bbox sebelum crop — crop
  longgar bisa ikut ngebawa teks lain (sisa "m4croNews" pernah ke-crop
  bareng logo M dan muncul nyempil di tengah bawah). Pakai scan grup kolom
  terang, ambil grup yang benar, crop persis bbox-nya.

## Pitfall poster (verified)
- **`vision_analyze` mengarang "garis tajam" pada gradient mulus.** Dua kali melaporkan
  potongan foto padahal profil baris turun 13.2 -> 3.0 -> 1.5 -> 0. Pakai
  `getBoundingClientRect` + profil baris piksel; vision cuma buat "kerasa sesak/kosong".
- **`image_generate` bisa gagal karena billing** (HTTP 402 insufficient_funds). Bukan
  API key yang hilang — jatuh ke gambar sumber, lalu Commons, lalu grafik CSS.
- **Openverse sering HTTP 500.** Wikimedia Commons lewat `scripts/fetch_commons.py`
  jalur gratis yang jalan. URL thumb manual ditolak ("Use thumbnail sizes listed") —
  pakai `thumburl` dari API.
- **Satu `@font-face` per weight, nama family sama.** Face 900-only + `font-weight: 600`
  tetap render 900 (mapping naik). Deklarasikan 400/600/700/800/900.
- **`h1` punya default UA `font-weight: 700`** yang menimpa inherit — set eksplisit di
  `.headline`.
- **`var()` yang tokennya dihapus me-invalidasi seluruh deklarasi** -> jatuh ke nilai
  awal (`opacity: 1` untuk glow). Grep `:root` vs semua `var(--...)` sebelum kirim.
- **Skala pratinjau jangan mengubah hasil ekspor.** `transform: scale()` bikin layout box
  tetap 1080px (scroll horizontal di HP). Bungkus `.stage` dengan ukuran
  `calc(canvas * var(--fit))` dan kunci `--fit: 1` saat viewport >= kanvas.
- **Nama file foto salah = gagal senyap.** Template memuat `assets/photo-graded.png`;
  kasih nama lain dan blok foto kosong padahal semua angka lain normal.
  `images_ok: false` dari `scripts/poster_checks.js` itu tandanya.
- **Jangan clipping teks biar muat.** Pendekkan barisnya, jangan potong kalimat.
- **Video sumber tidak perlu diunduh penuh.** `ffmpeg -ss 36 -i "<url mp4>" -frames:v 1`
  memakai HTTP range request: 1 frame 4K keluar dalam ~2 detik, bukan 114 MB.
  Cek `Content-Length` dulu (HEAD) biar tahu angkanya sebelum menyentuh file besar.
- **Frame video hampir selalu punya teks/label bawaan** (chip model, progress bar, UI).
  Crop band atas/bawah (mis. 10%-86% tinggi) sampai bersih, jangan biarkan teks video
  bertabrakan dengan headline poster.
- **`Page.captureScreenshot` timeout 5s kalau di call yang sama dengan `js()`/reload.**
  Pisah: call 1 reload + asersi, call 2 `cdp('Page.captureScreenshot')` sendirian.
  Kalau tetap timeout, ulang sekali — layer sudah ter-cache dan langsung sukses.
- **Foto siang hari bikin poster washed out.** `grade_photo.py --gain 0.45` (ditambah
  gamma ~1.35) menurunkan luminance baris atas dari ~100 ke ~55, baru setara house style.
- **Gear/logo putih di atas area foto terang kehilangan tepi** (bukan terpotong).
  Kasih `filter:drop-shadow(...)` di elemennya, jangan pindahkan posisinya.
- **`browser_exec` mati dengan "no registered browser plugin has that name".**
  `browser.cloud_provider: nous` menunjuk plugin cloud yang tidak terdaftar. Fix:
  `hermes config set browser.cloud_provider local` (langsung jalan lagi, sudah dicek).
- **Chrome/Edge sistem bisa crash "Abnormal renderer termination" di halaman poster**
  (headless CLI, halaman `file://` + transform + blend). Bukan bug CSS kita: halaman
  yang sama render normal di Chromium Playwright. Pakai
  `python scripts/render_shell.py index.html poster.png` — otomatis memilih
  `chrome-headless-shell` Playwright, lalu fallback Chrome/Edge sistem.
- **`file://` menyajikan gambar lama dari cache.** Ganti `photo-graded.png` lalu render
  ulang, hasilnya masih crop lama (peci tetap "kepotong"). Selalu
  `Network.setCacheDisabled(true)` + URL `?nc=<n>` tiap render ulang.
- **Potret resmi biasanya nyaris tanpa headroom** (kepala ~3% dari tepi atas). Crop apa pun
  bikin peci menempel bingkai. Kasih `transform:translateY(48px) scale(1.12)` di
  `.photo img` dan turunkan `--vignette` ke ~0.12-0.26 supaya latar di atas kepala
  masih terang dan siluet peci kebaca.

## Research & Caption IG (BAGIAN DARI OUTPUT — bukan opsional)
Setiap request video WAJIB menghasilkan video + caption IG sekaligus.
Baca `references/caption-research.md` sebelum nulis caption.

Alur lengkap satu request:
1. Render video (xnews.py + render.py) — verifikasi visual pakai
   vision_analyze sebelum lapor
2. Research berita pakai `web_search` tool Hermes (gratis, tanpa API key)
   — cari konteks dari judul video, verifikasi dari 2-3 sumber independen
3. Tulis caption pakai template gaya m4cro.news (paragraf fakta →
   konteks → analisis → "Gimana nih pendapat mu?" → CTA follow →
   hashtag #news #ekonomi #geopolitik #fyp). Contoh lengkap ada di
   file referensi.
4. Kirim ke user: MEDIA:<video> + teks caption siap copy-paste ke IG

## Verification
Poster: jalankan `scripts/poster_checks.js` di `browser_exec` — harus `canvas_ok: true`,
`poster_at_origin: true`, `overflow: [0, 0]`, `line_wraps` semua 1, `images_ok: true`,
`fonts_loaded` dua-duanya true. Lalu pastikan file ekspor benar 1080x1350 (Pillow).
Video: render testsrc2 5s, ffprobe stream duration harus 5.0s & nb_frames~150,
lalu vision_analyze frame: judul atas (regular) / 16:9 tengah-atas /
sumber+tanggal kiri bawah video / logo gear kiri atas / logo M kanan bawah
/ glow kiri bawah / bg hitam bersih.
