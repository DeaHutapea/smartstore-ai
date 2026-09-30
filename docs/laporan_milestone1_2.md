# Laporan Praktikum Proyek Terpadu — Milestone 1 dan 2

## Identitas

| Data | Isi |
|---|---|
| Mata kuliah | 10S3001 — Artificial Intelligence / Kecerdasan Buatan |
| Judul proyek | SmartStore AI: Pencarian Harga dan Optimasi Keranjang |
| Kelompok | Grup 14 |
| Program studi | Sarjana Sistem Informasi, Institut Teknologi Del |
| Dosen pengampu | Samuel Indra Gunawan Situmeang |
| Semester | Gasal 2026/2027 |
| Repositori GitHub | [DeaHutapea/smartstore-ai](https://github.com/DeaHutapea/smartstore-ai) |
| Branch | `main` |
| Tag Milestone 2 | `v0.2-milestone2` — belum tersedia per 30 September 2026 |

### Anggota kelompok

| Anggota | NIM |
|---|---|
| Fredrick Laurensius Aritonang | 12S24001 |
| Rospika Sarah Yosefin Siregar | 12S24008 |
| Dea Anggreany Hutapea | 12S24053 |

## Ringkasan

Proyek ini menyelesaikan dua submasalah rekomendasi belanja. Milestone 1
mencari penjual dan rute distribusi dengan biaya produk plus ongkir
minimum menggunakan Uniform Cost Search (UCS) dan A*. Milestone 2 memilih
penjual untuk setiap produk di keranjang dengan batasan tenggat, rentang
waktu kedatangan, dan budget menggunakan CSP.

Semua angka pada katalog yang tersedia saat ini merupakan **data simulasi
yang tertanam di kode**, bukan dataset marketplace eksternal. Harga dan
ongkir dinyatakan dalam ribuan Rupiah; karena itu nilai `267` berarti
Rp267.000. Kesimpulan eksperimen hanya berlaku untuk graf dan katalog
contoh tersebut.

## 1. Milestone 1 — Problem Framing dan Baseline Search

### 1.1 Masalah bisnis

Pelanggan tidak cukup membandingkan harga barang: pilihan termurah harus
menghitung harga produk dan seluruh ongkir pada rute dari gudang penjual ke
kota tujuan. Untuk contoh Speaker Bluetooth SoundMax X1, pelanggan berada
di Malang dan dapat memilih empat penjual yang gudangnya berada di Jakarta,
Semarang, Surabaya, atau Yogyakarta.

### 1.2 Formulasi ruang keadaan

- **State space (X):** `START`, satu keadaan virtual untuk setiap pilihan
  penjual, serta keadaan kota pada graf distribusi. Keadaan virtual penjual
  menyimpan identitas keputusan dan dipetakan ke kota gudangnya.
- **Actions (A):** dari `START`, pilih penjual; dari keadaan penjual/kota,
  kirim paket ke kota tetangga yang tersambung langsung.
- **Transition (T):** `START -> penjual P`; dari penjual P, ekspansi rute
  menggunakan graf yang berangkat dari kota gudang P.
- **Goal test (G):** posisi fisik keadaan sama dengan kota tujuan.
- **Path cost (C):** harga produk pada aksi pemilihan penjual ditambah
  seluruh biaya sisi distribusi pada rute.

UCS memberi prioritas pada biaya kumulatif `g(n)`. A* menggunakan
`f(n) = g(n) + h(n)`, dengan `h(n)` berupa jarak Haversine ke kota tujuan
yang dikalikan skala konservatif `0.07`; `h(START) = 0`.

### 1.3 Hasil eksperimen

Tujuan: Malang. Seluruh biaya pada tabel dalam ribuan Rupiah.

| Penjual awal | Harga produk | Ongkir rute termurah | Total |
|---|---:|---:|---:|
| TokoAndi (Jakarta) | 250 | 67 | 317 |
| GadgetPro (Semarang) | 235 | 32 | **267** |
| MegaStore (Surabaya) | 260 | 10 | 270 |
| BudiElektronik (Yogyakarta) | 245 | 24 | 269 |

UCS dan A* sama-sama memilih GadgetPro dengan rute Semarang–Surabaya–Malang
dan total **Rp267.000**. Pada run demo lokal, UCS mengekspansi 12 node dan
A* mengekspansi 7 node.

### 1.4 Validasi

Pengujian memeriksa bahwa UCS dan A* menghasilkan biaya sama, A* tidak
mengembangkan lebih banyak node pada contoh, dan tujuan di kota gudang
penjual menghasilkan ongkir nol. Sebuah pengujian tambahan menghitung
shortest path dengan Dijkstra untuk semua pasangan kota dan memastikan
heuristik tidak melebihi biaya aktual; konsistensi heuristik juga diuji
pada sisi graf saat ini. Bukti ini berlaku untuk graf contoh dan perlu
dijalankan lagi jika koordinat, graf, atau skala heuristik berubah.

## 2. Milestone 2 — Business Constraint Solver

### 2.1 Formulasi CSP

- **Variabel:** satu variabel keputusan untuk setiap produk dalam
  keranjang.
- **Domain:** penawaran (`Offer`) untuk produk tersebut, berisi nama
  penjual, harga, kota gudang, dan estimasi hari pengiriman.
- **Unary constraint:** setiap penawaran harus memenuhi
  `delivery_days <= deadline_days`.
- **Binary constraint:** untuk setiap pasangan produk,
  `abs(hari_i - hari_j) <= 2`.
- **Global constraint:** biaya lengkap tidak boleh melebihi budget.
- **Objective:** minimalkan jumlah harga produk ditambah ongkir penjual
  unik yang digunakan. Ongkir penjual adalah nol jika belanja dari penjual
  tersebut mencapai Rp4.700.000; selain itu dikenakan Rp20.000.

Solver menerapkan node consistency, AC-3, Backtracking dengan MRV,
Least-Constraining Value (LCV), forward checking, serta branch-and-bound.
Pencabangan dipangkas dengan batas bawah harga termurah domain tersisa dan
ongkir minimum yang pasti masih harus dibayar.

### 2.2 Hasil skenario utama

Input: Laptop, Mouse, Keyboard; budget Rp5.200.000; deadline 6 hari.

| Produk | Penjual terpilih | Harga | Hari |
|---|---|---:|---:|
| Laptop | GadgetPro | 4.350 | 5 |
| Mouse | BudiElektronik | 130 | 4 |
| Keyboard | BudiElektronik | 280 | 4 |
| **Jumlah harga** |  | **4.760** |  |
| Ongkir GadgetPro + BudiElektronik |  | **40** |  |
| **Total** |  | **4.800** |  |

Angka dalam ribuan Rupiah. Selisih waktu kirim terbesar adalah 1 hari,
deadline dipenuhi, dan total Rp4.800.000 berada dalam budget. Pengujian
kasus kecil juga membandingkan hasil solver dengan enumerasi brute-force
untuk memeriksa optimalitas.

### 2.3 Kasus infeasible

- Deadline 1 hari: tidak ada penawaran Laptop yang memenuhi batas unary;
  solver melaporkan `infeasible`.
- Budget Rp10.000 dengan deadline 10 hari: tidak ada kombinasi dengan
  biaya total dalam budget; solver melaporkan `infeasible`.

## 3. Analisis Sensitivitas Milestone 2

Eksperimen mengukur median lima run lokal menggunakan Python 3.11.16.
Setiap produk tambahan memiliki tiga penawaran sintetis; jumlah pilihan
meningkat secara eksponensial sebelum pemangkasan oleh batasan. Nilai
waktu bergantung pada perangkat dan beban sistem, sehingga ukur ulang pada
lingkungan final sebelum dimasukkan sebagai klaim performa umum.

| Produk | Penawaran/variabel | Median waktu (5 run) | Node dikunjungi |
|---:|---:|---:|---:|
| 3 | 3 | 0,09 ms | 14 |
| 6 | 3 | 0,65 ms | 74 |
| 9 | 3 | 19,02 ms | 578 |
| 12 | 3 | 205,25 ms | 4.996 |

Waktu dan jumlah node meningkat seiring ukuran masalah, namun untuk
generator data uji ini 12 produk selesai dalam sekitar 0,21 detik pada
mesin pengujian. Hasil ini bukan jaminan performa untuk katalog atau
kendala bisnis yang berbeda.

## 4. Pengujian dan Reproduksi

Di direktori proyek:

```powershell
uv sync
uv run pytest -v
uv run python src/search/price_search.py
uv run python src/csp/cart_solver.py
```

Hasil verifikasi pada sesi penyusunan draf: **10 test lulus**. Demo search
melaporkan biaya minimum Rp267.000 (UCS/A*); demo CSP melaporkan biaya
optimum Rp4.800.000 pada skenario utama.

## 5. Batasan dan pekerjaan sebelum penyerahan

1. Data saat ini sintetis dan tertanam di modul; belum ditemukan berkas
   dataset terpisah di workspace. Jika tim punya data lain, dokumentasikan
   sumber, satuan, tanggal pengambilan, dan cara anonimisasi sebelum
   mengganti data contoh.
2. Graf biaya rute Milestone 1 dan estimasi hari/biaya penjual Milestone 2
   adalah dua input simulasi terpisah; belum ada integrasi sumber logistik
   nyata.
3. Aturan gratis ongkir dan pengiriman adalah asumsi model untuk praktikum,
   bukan kebijakan marketplace yang telah divalidasi.
4. Repositori GitHub kelompok dapat diakses pada tautan di bagian
   Identitas, dan file `LICENSE` pada repositori menyatakan lisensi MIT.
   Pastikan lisensi ini sesuai dengan keputusan seluruh anggota.
5. Tag `v0.2-milestone2` belum ditemukan pada repositori per 30 September
   2026. Buat tag setelah versi yang akan dikumpulkan sudah disepakati,
   lalu tambahkan tautan tag tersebut pada salinan laporan yang diserahkan.
6. Ekspor laporan sesuai format dan nama berkas yang diminta pada instruksi
   tugas. Jika Milestone 1 dan 2 dikumpulkan sebagai berkas terpisah,
   simpan bagian Milestone 1 dan Milestone 2 masing-masing sebagai
   `Grup14-Tugas01.pdf` dan `Grup14-Tugas02.pdf`.

## 6. Kesimpulan

Pada data contoh, search berbobot menemukan penjual termurah setelah
ongkir, dan CSP menemukan alokasi keranjang minimum yang memenuhi
deadline, keseragaman waktu kedatangan, serta budget. Pengujian
heuristik, brute-force untuk kasus kecil, kasus infeasible, dan analisis
sensitivitas mendukung hasil implementasi. Kelayakan untuk data riil
memerlukan validasi katalog, satuan biaya, aturan pengiriman, serta
benchmark ulang.
