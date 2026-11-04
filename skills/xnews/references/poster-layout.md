# Layout poster 4:5 — angka hasil ukur

Template: `templates/poster-4x5.html` (1080x1350). Semua angka di bawah diukur dari
DOM render (`getBoundingClientRect`), bukan perkiraan. Ubah di token `:root`, jangan di
aturan komponen.

## Zona

| Zona | Nilai | Catatan |
|---|---|---|
| Kanvas | 1080 x 1350 | 4:5 feed IG |
| Foto | y 0-800, `object-fit: cover`, `object-position: 56% 26%` | 59% tinggi |
| Fade foto | transparan 66% -> .42 @82% -> .88 @93% -> hitam 100% | tidak boleh ada tepi keras |
| Logo M | tinggi 68px, center x=540, y 726-794 | aset 80x78, jangan > 90px |
| Headline | 4 baris, mulai y 844, blok 320px, lebar maks 880px | 1 baris = 1 client rect |
| Gear-$ | 118x100px di (44,44) | kiri atas |
| Glow | 470x360 di (0,990), `mix-blend-mode: screen` | kiri bawah, mask radial `at 0% 100%` |
| Handle | 21px, weight 400, center, bottom 46px | watermark jangan bold |
| Grain | seluruh kanvas, opacity .16, blend overlay | tekstur film |

## Tipografi

| Peran | Nilai |
|---|---|
| Family | Montserrat woff2 lokal (`assets/montserrat-<weight>.woff2`, 400 & 800 yang dipakai) |
| Headline | 800, 86px, line-height 0.93, letter-spacing -0.015em, UPPERCASE |
| Baris aksen | warna `--accent`, bobot sama (800) |
| Handle | 400, 21px, letter-spacing .05em |
| Lebar huruf | ~53px/karakter di 86px -> 880px muat ~15 karakter |

`h1` membawa default UA `font-weight: 700`; tanpa `font-weight` eksplisit di `.headline`
hasilnya 700, bukan 800.

## Warna

| Token | Nilai | Kontras di hitam |
|---|---|---|
| `--ink` | `#ffffff` | 21:1 |
| `--accent` biru | `#156ead` | 3.87:1 (aman >=24px, tidak untuk teks kecil) |
| `--accent` hijau | `#3FA600` | 6.67:1 |
| Hijau referensi asli | `rgb(93,249,3)` | 15:1 (terlalu menyala) |

## Keputusan user yang sudah final

- Branding "CW" + kotak hijau diganti logo M.
- Handle di tengah bawah, tanpa border/background, TIDAK bold (400).
- Gear-$ di KIRI ATAS (bukan kanan atas).
- Glow kiri bawah TANPA opacity (full), diatur lewat `--glow-w` + mask.
- Headline Montserrat ExtraBold (800), semua baris bobot sama.
- Aksen terakhir biru `#156ead`.
- Kalau foto dari sumber pihak ketiga: tulis kredit + lisensi di komentar HTML.
