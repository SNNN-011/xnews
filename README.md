# xnews — berita dari X/link → video reels 9:16 atau poster 4:5

Satu skill, dua bentuk output, dua-duanya keluar bareng caption IG gaya m4cro.news:

| Mau apa | Input | Output |
|---|---|---|
| **Video reels 9:16** | X/Twitter (video) | `output/<id>.mp4` 1080x1920: video 16:9 di atas-tengah, judul dari tweet, kredit sumber + tanggal, branding channel (gear-$, logo M, glow) |
| **Poster 4:5** | X post, blog, web, artikel (link apa pun) | `poster.png` 1080x1350: foto + headline besar, branding sama, siap feed IG |

**Langkah 0 — tanya dulu.** Kalau user belum menyebut bentuknya, agent tanya satu
pertanyaan: *"Mau dibikin poster (gambar 4:5) atau video reels (9:16)?"* Baru jalan
ke pipeline yang sesuai. Kalau sudah disebut, langsung kerjakan.

## Quick start

### 1. Install semua requirement (otomatis)

```bash
python skills/xnews/scripts/setup.py
```

Script ini install Pillow, numpy, yt-dlp, dan cek ffmpeg + aset template.
Aman dijalankan berulang.

**Yang perlu manual:**
- **ffmpeg** — Windows: `winget install Gyan.FFmpeg` | Mac: `brew install ffmpeg` | Linux: `sudo apt install ffmpeg`
- **Deepgram API key** (opsional) — hanya kalau tweet kosong dan judul
  harus diambil dari transkrip audio. Daftar gratis di [deepgram.com](https://deepgram.com),
  lalu set env `DEEPGRAM_KEY` atau taruh di `~/.deepgram_key`

### 2. Jalankan

```bash
python skills/xnews/scripts/xnews.py https://x.com/user/status/xxxxx
```

- Video ≤3 menit → render full
- Video >3 menit → dipotong per 60 detik (bisa diatur `--seg 30`)
- Output: `output/<video-id>.mp4` (1080x1920, siap upload TikTok/Reels/Shorts).
  File sementara (video sumber, frame, overlay PNG) otomatis dihapus setelah
  render, jadi folder output hanya berisi video final.

### Opsi

```bash
python skills/xnews/scripts/xnews.py <url> --seg 45 --out hasil/ --title "Judul Bahasa Indonesia" --wmsrc "CNN"
```

| Flag | Default | Fungsi |
|------|---------|--------|
| `--seg` | 60 | Panjang segmen kalau video >3 menit |
| `--out` | `output/` | Folder tujuan |
| `--title` | (teks tweet) | Override judul — dipakai agent buat judul Bahasa Indonesia hasil translate |
| `--wmsrc` | (kosong) | Nama sumber dari watermark di video — dipakai agent yang lihat frame |

**Judul:** otomatis Title Case (tiap kata huruf pertama kapital, termasuk
kata sambung). Script render pakai teks tweet apa adanya. Agent Hermes
yang translate judul ke Bahasa Indonesia pakai LLM-nya sendiri, lalu
render ulang dengan `--title "judul Indonesia"`.

**Sumber (baris SC):** agent Hermes lihat frame video (vision) buat cari
watermark sumber asli — video repost dari YouTube biasanya ada. Kalau ada,
agent render ulang dengan `--wmsrc "NamaSumber"`:

| Kondisi | Baris SC di video |
|---------|-------------------|
| X, tanpa WM | `SC: X@handle` |
| X, ada WM | `SC: NamaSumber X@handle` |
| YouTube, tanpa WM | `SC: Nama Channel` |
| YouTube, ada WM | `SC: NamaSumber` |

Script `xnews.py` tidak bisa baca watermark sendiri — itu kerjaan agent.

## Quick start poster (4:5)

Poster dirender sebagai HTML/CSS lalu diekspor PNG lewat browser — bukan ffmpeg.
Tidak butuh ffmpeg, yt-dlp, atau API key.

```bash
# 1. siapkan project (path relatif — Python native tidak paham /c/... atau ~/...)
mkdir -p poster-berita/assets

# 2. foto: dari link dulu; kalau link tidak punya gambar, cari di Commons
python skills/xnews/scripts/fetch_commons.py "trading floor" --get 3 --out poster-berita/source.png

# 3. grade fotonya (tonemap + tint + vignette, hasil ke file baru)
python skills/xnews/scripts/grade_photo.py poster-berita/source.png poster-berita/assets/photo-graded.png

# 4. copy template + aset
cp skills/xnews/templates/poster-4x5.html poster-berita/index.html
cp skills/xnews/assets/{logoM.png,gear.png,glow.png,montserrat-400.woff2,montserrat-800.woff2} poster-berita/assets/
```

Lalu agent: ganti 4 baris headline + handle + `--accent`, render 1080x1350 di browser,
jalankan `skills/xnews/scripts/poster_checks.js` sebagai asersi, ekspor `poster.png`.
Angka layout lengkap ada di `skills/xnews/references/poster-layout.md`.

## Output: Poster + Caption IG

Poster juga wajib keluar bareng caption IG — spesifikasi captionnya sama dengan video
(`skills/xnews/references/caption-research.md`).

## Output: Video + Caption IG

Setiap pemrosesan menghasilkan **dua hal sekaligus**:

1. **Video 9:16** siap upload (`output/<video-id>.mp4`)
2. **Caption IG** lengkap (dari Hermes Agent setelah riset berita via
   `web_search` built-in — gratis tanpa API key) dengan gaya m4cro.news:
   fakta → konteks → analisis → CTA → hashtag

User tinggal upload video + copy-paste caption ke IG. Template dan contoh
ada di `skills/xnews/references/caption-research.md`.

## Untuk user Hermes Agent

Repo ini juga berupa skill Hermes. Install:

```bash
cp -r skills/xnews ~/.hermes/skills/xnews   # atau path skills Hermes kamu
```

Skill akan otomatis jalanin `setup.py` kalau ada requirement yang belum ada.
Poster tidak butuh `setup.py` — cuma Pillow + numpy + browser Chromium yang sudah ada
di mesin Hermes.

## Kustomisasi

- **Ganti logo/branding:** timpa file di `skills/xnews/assets/`
  (PNG transparan — ukuran bebas, auto-resize)
- **Ganti posisi/ukuran elemen:** edit konstanta di
  `skills/xnews/scripts/render.py` (VID_TOP, TITLE_ZONE_*, SRC_Y, dll)
- **Ganti font:** taruh TTF baru di `assets/`, edit `_load()` di render.py
- **Poster:** edit token `:root` di `skills/xnews/templates/poster-4x5.html`
  (`--headline-size`, `--accent`, `--photo-h`, `--glow-w`, `--mark-h`) — jangan edit
  aturan komponen, biar satu perubahan jalan ke seluruh layout

## Requirement

- Python 3.9+
- ffmpeg + ffprobe (di PATH)
- yt-dlp (auto-install via setup.py)
- Pillow + numpy (auto-install via setup.py)
- Poster saja: browser Chromium (sudah ada di Hermes) — tanpa ffmpeg/yt-dlp

## License

MIT

<!-- cache-buster -->
