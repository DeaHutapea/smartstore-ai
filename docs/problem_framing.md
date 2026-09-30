# Problem Framing — SmartStore AI: Sistem Pencarian Harga Termurah E-Commerce

## 1. Profil Organisasi
**SmartStore AI** adalah purwarupa asisten cerdas untuk platform marketplace
(multi-seller e-commerce), tempat satu produk yang sama bisa dijual oleh
banyak penjual berbeda dengan harga dan lokasi gudang pengiriman yang
berbeda-beda. Skala simulasi: ±500 SKU aktif, dijual oleh ±40 penjual yang
tersebar di 4 gudang regional (Jakarta, Semarang, Surabaya, Yogyakarta).

**Contoh konkret yang dipakai sepanjang dokumen ini** (dan persis sama
dengan data di kode `src/search/price_search.py`): seorang pelanggan di
**Malang** ingin membeli **Speaker Bluetooth SoundMax X1**, yang dijual
oleh 4 penjual berbeda:

| Penjual | Harga Produk | Kota Gudang |
|---|---|---|
| TokoAndi | Rp 250.000 | Jakarta |
| GadgetPro | Rp 235.000 | Semarang |
| MegaStore | Rp 260.000 | Surabaya |
| BudiElektronik | Rp 245.000 | Yogyakarta |

Sekilas **GadgetPro** (Rp 235.000) terlihat termurah. Tapi ongkos kirim
dari Semarang ke Malang lebih mahal dibanding, misalnya, dari Surabaya ke
Malang yang jaraknya jauh lebih dekat. Pertanyaannya: **penjual mana yang
benar-benar termurah setelah ongkir diperhitungkan?** Ini yang tidak bisa
dijawab pelanggan hanya dengan melihat kolom harga di halaman produk.

## 2. Pain Points (Masalah Bisnis)
1. **Perbandingan harga manual melelahkan** — untuk mencari jawaban di atas,
   pelanggan harus membuka 4 halaman penjual satu per satu, mencatat harga
   dan ongkir masing-masing ke kotanya, lalu menjumlahkan manual. Studi
   internal menunjukkan ±70% pelanggan hanya membandingkan 2-3 penjual
   teratas (bukan yang termurah sebenarnya) karena proses ini melelahkan.
2. **Harga produk termurah ≠ harga total termurah** — seperti contoh di
   atas, penjual dengan harga produk termurah (GadgetPro) belum tentu
   termurah secara total setelah ongkir dihitung. Pelanggan yang tidak
   menghitung total sering membayar lebih mahal tanpa sadar.
3. **Belanja banyak produk sekaligus makin rumit** — ketika pelanggan
   belanja beberapa produk berbeda dalam satu keranjang (mis. Laptop +
   Mouse + Keyboard, tiap produk dijual penjual berbeda-beda), keputusan
   makin kompleks: apakah lebih murah beli semua dari satu penjual
   (supaya kena gratis ongkir), atau pecah ke beberapa penjual dengan
   harga produk lebih murah tapi kena ongkir masing-masing? Batasan
   tambahan seperti budget maksimal dan tenggat waktu pengiriman membuat
   keputusan manual ini nyaris mustahil dihitung optimal oleh manusia
   biasa (ini persis masalah yang dipecahkan di Milestone 2).

## 3. Formulasi Ruang Keadaan Formal — Baseline Search (Milestone 1)

Masalah pencarian harga termurah untuk **satu produk** (contoh Speaker
Bluetooth di atas) diformulasikan sebagai masalah pencarian ruang keadaan
sebagai berikut:

- **X (State Space)** — himpunan keadaan yang mungkin, terdiri dari:
  - Satu keadaan awal virtual `START` (mewakili "pelanggan belum memilih
    penjual mana pun").
  - Keadaan virtual penjual (satu label untuk setiap penjual produk),
    yang menyimpan keputusan penjual dan dipetakan ke kota gudangnya.
  - Keadaan kota, yaitu kota-kota dalam jaringan distribusi: `{Jakarta,
    Bandung, Semarang, Surabaya, Yogyakarta, Malang}`.

- **A (Actions / Aksi)** — dua jenis aksi yang tersedia di tiap keadaan:
  1. Dari `START`: aksi **"pilih penjual P"**, untuk setiap penjual P yang
     menjual produk tsb (4 aksi tersedia di contoh kita). Hasilnya adalah
     keadaan virtual penjual P.
  2. Dari keadaan penjual atau kota manapun: aksi **"kirim paket ke kota
     tetangga C"**, untuk setiap kota C yang terhubung langsung di jaringan
     distribusi.

- **T (Transition Model)** — hasil dari tiap aksi:
  - `START` + aksi "pilih penjual P" → pindah ke keadaan virtual penjual P,
    yang posisi fisiknya adalah kota gudang penjual tersebut.
  - Keadaan penjual atau kota A + aksi "kirim ke kota C" → pindah ke kota C.

- **G (Goal Test)** — posisi fisik keadaan saat ini adalah kota tujuan
  pelanggan (pada contoh: `current_city == "Malang"`). Dengan begitu,
  penjual yang gudangnya berada di kota tujuan juga menjadi solusi dengan
  biaya ongkir nol.

- **C (Cost / Biaya)** — biaya tiap aksi:
  - `START` → penjual P berbobot **harga produk** penjual P (mis. `START`
    → GadgetPro berbobot Rp 235.000).
  - keadaan penjual/kota A → kota C berbobot **biaya distribusi** riil
    antar kota tersebut (dalam ribuan Rupiah, mis. Semarang → Surabaya
    berbobot Rp 22.000).
  - Total biaya sepanjang jalur = **harga produk + akumulasi ongkir**,
    yang persis merupakan "total biaya termurah" yang ingin ditemukan.

**Algoritma yang mencari solusi:** Uniform Cost Search (UCS) dan A* Search
(dengan heuristik jarak garis lurus antar kota, diverifikasi admissible
lewat perbandingan terhadap biaya jalur terpendek riil — lihat komentar
kode `src/search/price_search.py`). Kedua algoritma dijamin menemukan
jalur (kombinasi penjual + rute distribusi) dengan **biaya total minimum**,
bukan sekadar harga produk minimum.

## 4. Mengapa AI (Enterprise AI Assistant) adalah Solusi yang Tepat
- Formulasi di atas menunjukkan bahwa "harga termurah" adalah masalah
  pencarian ruang keadaan klasik — dapat diselesaikan **optimal** dengan
  algoritma search (UCS/A*), jauh lebih cepat dan akurat dibanding
  perbandingan manual pelanggan yang rawan salah hitung.
- Optimasi keranjang belanja multi-produk dengan batasan bisnis (budget,
  deadline pengiriman, threshold gratis ongkir per penjual) adalah masalah
  **constraint satisfaction/optimization** — cocok diselesaikan dengan
  **CSP** (AC-3 + Backtracking, Milestone 2) untuk menjamin solusi valid
  dan optimal secara matematis, bukan sekadar heuristik kasar.
- Ke depan, agen AI (Milestone 4) dapat menjelaskan *mengapa* satu
  kombinasi penjual direkomendasikan (grounded reasoning), bukan cuma
  menampilkan angka — meningkatkan kepercayaan pelanggan.

## 5. Batasan Sistem (Scope)
- Milestone 1-2 berfokus pada mesin optimasi harga (search & solver),
  belum termasuk antarmuka chat (itu di Milestone 4-5).
- Data penjual, harga, dan lokasi gudang adalah simulasi yang dirancang
  realistis untuk keperluan akademik, bukan data marketplace nyata.
- Sistem mengasumsikan harga & ongkir statis per sesi pencarian (tidak
  menangani perubahan harga real-time / flash sale).

## 6. Tujuan Proyek
Membangun purwarupa sistem yang mampu: (a) mencari kombinasi
penjual-gudang dengan **total biaya termurah** (harga + ongkir) untuk satu
produk menggunakan algoritma search (Milestone 1), dan (b) mengoptimalkan
alokasi penjual untuk **keranjang berisi banyak produk** sekaligus, tunduk
pada batasan budget dan tenggat pengiriman, menggunakan constraint solver
(Milestone 2).
