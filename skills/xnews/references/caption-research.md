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

## Template caption (gaya m4cro.news)

**Struktur WAJIB (dari analisis 4 contoh post asli):**

```
[Paragraf 1: fakta utama — apa terjadi, siapa, di mana, kapan]
[1-2 kalimat, langsung to the point]

[Paragraf 2: konteks/detail tambahan]
[Angka, data, timeline, atau info pendukung]

[Paragraf 3: analisis singkat / implikasi]
[Kenapa ini penting — dampak, pelaku, sasaran]

[Opsional: kutipan langsung dalam tanda kutip + atribusi]

Gimana nih pendapat mu?

Butuh berita makroekonomi atau geopolitik. Jangan lupa follow @m4cro.news untuk informasi lainnya

#news #ekonomi #geopolitik #fyp
```

**Aturan gaya:**
- Bahasa Indonesia jurnalistik, kalimat lengkap, TANPA emoji
- Angka ditulis: "42%", "3,5 juta ton", "8 dari 12 tangki"
- Nama orang/tempat apa adanya (Donald Trump, Novoshakhtinsk, Rostov)
- Penutup WAJIB persis: "Gimana nih pendapat mu?" lalu CTA follow + hashtag standar
- Tidak ada penanda sumber di caption — sumber ada di video (SC: X @handle)

## Contoh nyata (video Novoshakhtinsk)

```
Tangki penyimpanan lain meledak di terminal penyaluran minyak milik Pabrik Produk Minyak Novoshakhtinsk di wilayah Rostov, Rusia. Rekaman video dari kanal monitoring Exilenova+ menunjukkan kolom api menjulang puluhan meter di atas lokasi pada malam 13 Oktober.

Terminal tersebut telah diserang drone pada 10 Oktober dan sejak itu terus dilanda kebakaran selama empat hari. Menurut analisis kanal OSINT ASTRA terhadap citra satelit, setidaknya delapan dari dua belas tangki di fasilitas tersebut telah rusak.

Terminal milik grup Yug Rusi memiliki kapasitas penyaluran hingga 3,5 juta ton produk minyak per tahun. Fasilitas ini digunakan untuk ekspor sekaligus pasokan bahan bakar bagi militer Rusia.

Penyebab ledakan terbaru belum diketahui dan pihak berwenang Rusia hingga kini belum memberikan komentar resmi. Peristiwa ini terjadi beberapa jam setelah Presiden AS Donald Trump mengumumkan kesepakatan penjualan diesel Rusia bersama Presiden Vladimir Putin.

Ukraina telah menargetkan kilang minyak dan infrastruktur energi Rusia secara berulang dalam upaya memutus pasokan bahan bakar militer dan menekan pendapatan energi Moskow.

Gimana nih pendapat mu?

Butuh berita makroekonomi atau geopolitik. Jangan lupa follow @m4cro.news untuk informasi lainnya

#news #ekonomi #geopolitik #fyp
```

## Requirement research

- **web_search tool** (built-in Hermes) — gratis, tanpa API key
- **web_extract tool** (built-in Hermes) — buat baca artikel lengkap kalau snippet kurang
- Tidak perlu Python package tambahan, tidak perlu API key eksternal
