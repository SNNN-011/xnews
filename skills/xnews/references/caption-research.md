# Research & Caption IG (m4cro.news style)

## Kapan pakai
User minta video dari X/Twitter di-render + dikasih caption buat posting IG.

## Alur research (agent lakukan, BUKAN script)

1. **Ambil judul** — dari teks tweet (sama seperti judul video).
2. **Web search** pakai tool Hermes (`web_search`):
   - Query 1: keyword judul (English) — e.g. "Novoshakhtinsk oil depot explosion Rostov"
   - Query 2: keyword judul (bahasa lokal) — e.g. "Новошахтинск нефтебаза взрыв"
   - Ambil 5-8 hasil, baca snippet/full text via `web_extract` kalau perlu.
3. **Verifikasi fakta** dari minimal 2-3 sumber independen. Catat:
   - Apa yang terjadi (fakta utama)
   - Angka/data penting (kapasitas, jumlah korban, persentase)
   - Konteks (kapan, di mana, siapa terlibat)
   - Siapa sumber (nama channel/akun/media)
   - **Teks caption tweet sumber** — buat kutipan paragraf terakhir

## Template caption (WAJIB — struktur v3)

**Struktur (dari analisis 5 post asli m4cro.news):**

```
[Paragraf 1: fakta utama — apa terjadi, siapa, di mana, kapan]
[1-2 kalimat, langsung to the point]

[Paragraf 2: konteks/detail tambahan]
[Angka, data, timeline, atau info pendukung]

[Paragraf 3: analisis singkat / implikasi]
[Kenapa ini penting — dampak, kapasitas, siapa terlibat]

"[kutipan dari caption tweet X sumber]" Mengutip (X@Handle)

Gimana nih pendapat mu?

Butuh berita makroekonomi atau geopolitik. Jangan lupa follow @m4cro.news untuk informasi lainnya

#news #ekonomi #geopolitik #fyp
```

**Aturan gaya:**
- Bahasa Indonesia jurnalistik, kalimat lengkap, TANPA emoji
- Angka ditulis: "42%", "3,5 juta ton", "8 dari 12 tangki"
- Nama orang/tempat apa adanya (Donald Trump, Novoshakhtinsk, Rostov)
- **Paragraf 1-3 = penjelasan** (analisis agent, bukan copy tweet)
- **Paragraf terakhir = KUTIPAN** dari caption tweet X sumber:
  - Dibungkus tanda kutip `"..."`
  - Isinya teks tweet sumber (diterjemahkan ke Bahasa Indonesia)
  - Atribusi di luar tanda kutip: `Mengutip (X@Handle)` — untuk sumber X/Twitter
- Penutup WAJIB persis: "Gimana nih pendapat mu?" lalu CTA follow + hashtag standar
- Tidak ada penanda sumber di caption — sumber ada di video (SC: X @handle)

## Variasi format atribusi (dari post asli)

| Sumber | Format atribusi |
|---|---|
| X/Twitter account | `Mengutip (X@HormuzReport)` |
| X/Twitter account | `Mengutip (X@FarsNews_Agency)` |
| Media militer | `Mengutip Media Militer Yaman (X@MMY1444)` |
| TV news | `Mengutip Fox News` / `Menurut laporan Fox News` |

Paling umum untuk sumber X: `Mengutip (X@Handle)`

## Contoh nyata (video Novoshakhtinsk)

```
Ledakan kembali terjadi di terminal penyaluran minyak Novoshakhtinsk di wilayah Rostov, Rusia. Kolom api menjulang puluhan meter di atas lokasi pada malam 13 Oktober.

Terminal tersebut telah diserang drone pada 10 Oktober dan sejak itu terus dilanda kebakaran selama empat hari. Menurut analisis kanal OSINT ASTRA terhadap citra satelit, setidaknya delapan dari dua belas tangki di fasilitas tersebut telah rusak.

Terminal milik grup Yug Rusi memiliki kapasitas penyaluran hingga 3,5 juta ton produk minyak per tahun. Fasilitas ini digunakan untuk ekspor sekaligus pasokan bahan bakar bagi militer Rusia. Penyebab ledakan terbaru belum diketahui dan pihak berwenang Rusia hingga kini belum memberikan komentar resmi.

"Tangki penyimpanan lain di depot minyak Novoshakhtinsk, yang diserang pada 10 Oktober, telah meledak di Rostov." Mengutip (X@Exilenova_plus)

Gimana nih pendapat mu?

Butuh berita makroekonomi atau geopolitik. Jangan lupa follow @m4cro.news untuk informasi lainnya

#news #ekonomi #geopolitik #fyp
```

## Requirement research

- **web_search tool** (built-in Hermes) — gratis, tanpa API key
- **web_extract tool** (built-in Hermes) — buat baca artikel lengkap kalau snippet kurang
- Tidak perlu Python package tambahan, tidak perlu API key eksternal
