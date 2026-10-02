# Etika, Privasi, dan Tata Kelola Data — SmartStore AI

Draf awal (QA, Evaluation & Ethics Lead). Akan diperdalam pada Bab 5 laporan
final. **Catatan:** rujukan regulasi di bawah perlu dicocokkan ulang dengan
teks resmi sebelum masuk laporan final.

## 1. Cakupan data saat ini
- Data penjual, harga, kota gudang, dan biaya kirim adalah **data simulasi**.
- Tidak ada data pribadi pelanggan (nama, alamat, kontak, riwayat belanja)
  yang disimpan atau diproses pada Milestone 1-2.
- Input pelanggan hanya produk, budget, dan deadline, tanpa identitas.

## 2. Keselarasan dengan UU PDP No. 27 Tahun 2022
| Prinsip | Kondisi sekarang | Jika sistem memakai data nyata |
|---|---|---|
| Minimisasi data | Hanya data yang dibutuhkan solver | Kumpulkan field yang diperlukan saja |
| Tujuan yang sah | Optimasi harga termurah | Nyatakan tujuan pemrosesan secara eksplisit |
| Persetujuan & transparansi | Tidak berlaku (tanpa data pribadi) | Wajib ada persetujuan dan pemberitahuan |
| Keamanan | Data hanya di repositori | Hindari menyimpan data pribadi di repo; pakai `.env` yang di-ignore |

## 3. Keselarasan dengan SE Menkominfo No. 9 Tahun 2023 (Etika Kecerdasan Artifisial)
- **Transparansi:** sistem menampilkan alasan keputusan (`reason` saat
  infeasible, rincian penjual dan biaya saat optimal).
- **Akuntabilitas:** keputusan akhir pembelian tetap pada pelanggan.
- **Keandalan:** hasil solver diverifikasi dengan test brute-force dan edge case.

## 4. Potensi bias dan mitigasinya
- Pengurutan murni berdasarkan harga dapat merugikan penjual kecil dengan
  harga sedikit lebih tinggi tetapi layanan lebih baik. Mitigasi: tampilkan
  alternatif, jangan hanya satu hasil.
- Data simulasi bisa tidak mewakili pasar nyata; jangan generalisasi
  kesimpulan eksperimen.
- Pada data nyata, periksa apakah penjual dari wilayah tertentu
  tersisih akibat ongkir semata.

## 5. Keamanan LLM (rencana Milestone 4 dan seterusnya)
- Input pengguna dibungkus delimiter `<<<USER_INPUT>>>` pada prompt agen.
- Uji serangan prompt injection (mis. "abaikan instruksi sebelumnya") dan
  catat hasilnya di laporan.
- Tool hanya menerima argumen terstruktur yang divalidasi; galat tool
  ditangani tanpa membocorkan detail internal.
- Batas iterasi maksimum pada siklus ReAct untuk mencegah loop tak berujung.

## 6. Kepatuhan penggunaan alat bantu AI dan sumber data
- Jika memakai data marketplace nyata, periksa syarat layanan situs sebelum scraping.
- Alat bantu AI (mis. Copilot) dipakai sebagai pendamping; setiap anggota
  harus memahami dan mampu menjelaskan kode yang di-commit.
