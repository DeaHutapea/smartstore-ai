# Pemodelan Matematis Formal — CSP Milestone 2 (Optimasi Keranjang Belanja)

## Contoh Kasus Konkret

Pelanggan punya keranjang berisi 3 produk: **Laptop, Mouse, Keyboard**.
Setiap produk dijual oleh beberapa penjual dengan harga, kota gudang, dan
estimasi lama pengiriman berbeda (data persis sama dengan
`src/csp/cart_solver.py`):

| Produk | Penjual | Harga | Kota | Lama Kirim |
|---|---|---|---|---|
| Laptop | TokoAndi | Rp 4.500.000 | Jakarta | 3 hari |
| Laptop | GadgetPro | Rp 4.350.000 | Semarang | 5 hari |
| Laptop | MegaStore | Rp 4.600.000 | Surabaya | 2 hari |
| Mouse | TokoAndi | Rp 150.000 | Jakarta | 3 hari |
| Mouse | BudiElektronik | Rp 130.000 | Yogyakarta | 4 hari |
| Mouse | MegaStore | Rp 160.000 | Surabaya | 2 hari |
| Keyboard | GadgetPro | Rp 300.000 | Semarang | 5 hari |
| Keyboard | BudiElektronik | Rp 280.000 | Yogyakarta | 4 hari |
| Keyboard | MegaStore | Rp 320.000 | Surabaya | 2 hari |

Pelanggan menetapkan: **budget maksimal Rp 5.200.000** dan **tenggat
pengiriman maksimal 6 hari**. Sistem harus memilih **satu penjual per
produk** yang memenuhi semua batasan dengan **total biaya seminimal
mungkin**.

## Pemodelan CSP Formal

- **Variables (Variabel Keputusan)** — satu variabel untuk setiap produk
  di keranjang: `X = {Laptop, Mouse, Keyboard}`.

- **Domain (Domain Nilai)** — untuk tiap variabel, domainnya adalah daftar
  opsi penjual yang menjual produk tsb. Setiap nilai domain adalah tuple
  `(penjual, harga, kota, lama_kirim)`. Contoh:
  `Domain(Laptop) = {(TokoAndi,4500,Jakarta,3), (GadgetPro,4350,Semarang,5),
  (MegaStore,4600,Surabaya,2)}`.

- **Constraints (Fungsi Batasan)** — tiga jenis batasan diterapkan:
  1. **Unary constraint (node consistency)** — untuk setiap opsi `o` di
     domain suatu variabel: `o.lama_kirim <= deadline_pelanggan`. Opsi
     yang melanggar dibuang dari domain **sebelum** pencarian dimulai
     (mis. jika deadline = 1 hari, semua opsi terbuang → infeasible sejak
     awal, tidak perlu backtracking).
  2. **Binary constraint (diselesaikan dengan AC-3)** — untuk setiap
     pasangan variabel `(Xi, Xj)` dan nilai yang dipilih `(oi, oj)`:
     `|oi.lama_kirim - oj.lama_kirim| <= 2` (semua produk dalam satu
     pesanan harus tiba dalam rentang waktu berdekatan, maksimal selisih
     2 hari — supaya pelanggan tidak menerima barang secara terpisah-pisah
     dalam waktu yang jauh berbeda).
  3. **Global constraint (dicek saat assignment lengkap, bukan arc)** —
     `total_biaya(assignment) <= budget_pelanggan`, di mana:
     ```
     total_biaya = Σ harga(produk) + Σ ongkir(penjual unik yang dipakai)
     ongkir(penjual) = 0,  jika total belanja dari penjual itu >= Rp 4.700.000
     ongkir(penjual) = Rp 20.000,  jika sebaliknya
     ```

- **Objective (Fungsi Tujuan, untuk versi optimasi)** — di antara semua
  assignment yang valid (memenuhi semua constraint di atas), pilih yang
  **meminimalkan** `total_biaya(assignment)`.

## Solusi untuk Contoh Kasus

Dengan budget Rp 5.200.000 dan deadline 6 hari, solver (AC-3 +
Backtracking MRV/LCV) menemukan solusi optimal:

| Produk | Penjual Terpilih | Alasan |
|---|---|---|
| Laptop | GadgetPro (Rp 4.350.000) | Harga termurah, lama kirim 5 hari (≤ 6 hari, valid) |
| Mouse | BudiElektronik (Rp 130.000) | Harga termurah, lama kirim 4 hari |
| Keyboard | BudiElektronik (Rp 280.000) | Sama penjual dengan Mouse → belanja digabung |

Verifikasi batasan biner: selisih lama kirim GadgetPro (5) vs BudiElektronik
(4) = 1 hari ≤ 2 hari → **valid**.

Total biaya: Rp 4.350.000 + Rp 130.000 + Rp 280.000 = Rp 4.760.000 (harga
produk). Karena belanja dari GadgetPro (Rp 4.350.000) dan dari
BudiElektronik (Rp 410.000) masing-masing di bawah threshold gratis ongkir
(Rp 4.700.000), dikenakan ongkir Rp 20.000 untuk **masing-masing** penjual
→ **total akhir = Rp 4.800.000** (≤ budget Rp 5.200.000 → valid & optimal).

## Mengapa CSP (bukan Genetic Algorithm)

Dipilih CSP karena:
1. Ruang solusi berukuran kecil-menengah dan **diskret murni** (kombinasi
   penjual per produk), bukan ruang kontinu — cocok untuk pencarian
   sistematis (backtracking), bukan pencarian stokastik (GA).
2. Kita butuh **jaminan solusi optimal terverifikasi**, bukan solusi
   "cukup baik" hasil evolusi beberapa generasi — CSP dengan
   branch-and-bound menjamin optimalitas matematis.
3. Batasan bisnis (budget, deadline, selisih waktu kirim) secara alami
   dinyatakan sebagai **constraint keras** (hard constraints) yang harus
   dipenuhi, bukan penalti lunak (soft penalty) seperti pada fitness
   function GA.
