# Spesifikasi PEAS — SmartStore AI: Sistem Pencarian Harga Termurah

## Performance Measure (Ukuran Kinerja)
Sistem dinilai berhasil jika:
- Menemukan kombinasi penjual-gudang dengan **total biaya (harga + ongkir)
  termurah yang benar secara matematis** (optimal, bukan aproksimasi),
  dapat diverifikasi lewat brute-force pada kasus kecil.
- Untuk keranjang multi-produk: menghasilkan alokasi penjual yang **valid**
  (memenuhi semua batasan: budget, deadline pengiriman) dan **seoptimal
  mungkin** (total biaya serendah mungkin di antara solusi valid).
- **Waktu komputasi** wajar (< beberapa detik) bahkan saat jumlah penjual/
  produk membesar (diukur lewat analisis sensitivitas Milestone 2).
- Gagal secara eksplisit (bukan diam-diam salah) ketika tidak ada solusi
  yang memenuhi batasan (mis. budget terlalu kecil).

## Environment (Lingkungan)
Lingkungan operasional: katalog produk multi-penjual, data harga & lokasi
gudang tiap penjual, graf biaya distribusi antar-kota, dan input pelanggan
(produk yang dicari / isi keranjang, budget, tenggat waktu).

Klasifikasi sifat lingkungan:
- **Fully observable** (untuk sesi pencarian ini) — seluruh harga, lokasi
  gudang, dan biaya distribusi diketahui penuh oleh sistem saat pencarian
  dijalankan (data statis per sesi, bukan tersembunyi).
- **Deterministic** — untuk kombinasi input yang sama, sistem selalu
  menghasilkan solusi yang sama; tidak ada faktor acak dalam pencarian.
- **Static** — harga & ongkir tidak berubah selama satu proses pencarian
  berlangsung (tidak menangani perubahan real-time).
- **Discrete** — ruang keadaan (penjual, gudang, kombinasi keranjang)
  bersifat diskret, bukan kontinu.
- **Single-agent** (dari sudut pandang solver) — solver menyelesaikan satu
  instance masalah pelanggan secara independen, tanpa interaksi/kompetisi
  dengan agen lain.

## Actuators (Aktuator / Cara Sistem Bertindak)
- Mengembalikan **rekomendasi kombinasi termurah** (penjual, gudang asal,
  rincian harga produk + ongkir) untuk pencarian satu produk.
- Mengembalikan **alokasi penjual per produk** untuk keranjang multi-produk
  yang memenuhi batasan, beserta total biaya dan bukti validitasnya.
- Melaporkan status **infeasible** (tidak ada solusi valid) jika batasan
  pelanggan (budget/deadline) tidak mungkin dipenuhi, disertai alasan.

## Sensors (Sensor / Cara Sistem Menerima Informasi)
- Input pelanggan: produk yang dicari atau daftar keranjang, kota tujuan,
  budget maksimal, tenggat waktu pengiriman.
- Data katalog: daftar penjual per produk beserta harga.
- Data logistik: graf biaya pengiriman antar gudang-kota, estimasi waktu
  tempuh per rute.
- Aturan bisnis: threshold minimum belanja per penjual untuk gratis ongkir.
