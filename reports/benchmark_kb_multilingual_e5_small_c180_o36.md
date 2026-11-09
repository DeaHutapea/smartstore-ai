# Benchmark `kb_multilingual_e5_small_c180_o36`

Model: `intfloat/multilingual-e5-small` · chunk=180 kata · overlap=36 · 302 chunk
Ambang OOD dari kalibrasi data dev terpisah: **0.850**.

| Tipe | n | Hit@1 | Hit@3 | MRR | Rata-rata skor top-1 |
|---|---|---|---|---|---|
| synonym | 8 | 1.00 | 1.00 | 1.00 | 0.877 |
| ambiguous | 3 | 0.67 | 1.00 | 0.78 | 0.874 |
| out_of_domain | 5 | – | – | – | 0.792 |

**Hasil holdout dengan ambang dev** — in-domain diterima 11/11, out-of-domain ditolak 5/5.
Precision penolakan OOD=1.000, recall=1.000, F1=1.000.

| ID | Tipe | Kueri | Top-1 | Skor | Ekspektasi | Rank |
|---|---|---|---|---|---|---|
| Q01 | synonym | Di Tokopedia, berapa lama dana refund masuk setelah pesanan dibatalkan? | MKT004 | 0.8964 | MKT004 | 1 |
| Q02 | synonym | Kenapa paket saya telat sampai melebihi perkiraan? | MKT001 | 0.8545 | MKT001 | 1 |
| Q03 | synonym | Penjual menolak keluhan saya, langkah apa yang bisa saya tempuh? | MKT002 | 0.8704 | MKT002 | 1 |
| Q04 | synonym | Voucher bebas biaya kirim bisa dipakai di jenis toko apa saja? | MKT003 | 0.8692 | MKT003,MKT008 | 1 |
| Q05 | synonym | Apa hak pembeli jika barang yang diterima tidak sesuai perjanjian? | REG001 | 0.8565 | REG001 | 1 |
| Q06 | synonym | Kewajiban penyelenggara platform dalam menjaga kerahasiaan data pribadi pengguna | REG003 | 0.8989 | REG003 | 1 |
| Q07 | synonym | Berapa hari batas waktu retur barang di Shopee Mall? | MKT006 | 0.8839 | MKT005,MKT006 | 1 |
| Q08 | synonym | Kewajiban pelaku usaha yang berdagang lewat sistem elektronik | REG002 | 0.8876 | REG002 | 1 |
| Q09 | ambiguous | Bagaimana kebijakan pengembalian? | MKT005 | 0.8784 | MKT004,MKT005,MKT007 | 1 |
| Q10 | ambiguous | Aturan soal pengiriman barang | MKT008 | 0.8827 | MKT001,MKT003,REG004 | 3 |
| Q11 | ambiguous | Syarat dan ketentuan | MKT008 | 0.8605 | MKT007,MKT008 | 1 |
| Q12 | out_of_domain | Resep nasi goreng seafood yang enak | MKT003 | 0.8098 | – | – |
| Q13 | out_of_domain | Siapa juara Liga Champions musim lalu? | REG004 | 0.7677 | – | – |
| Q14 | out_of_domain | Cara install Python di Windows 11 | REG003 | 0.7954 | – | – |
| Q15 | out_of_domain | Prakiraan cuaca besok di Medan | REG004 | 0.8163 | – | – |
| Q16 | out_of_domain | Apa itu teori relativitas Einstein? | REG001 | 0.7725 | – | – |

Catatan: angka OOD dihitung pada set evaluasi holdout. Ukuran set kecil, jadi hasil ini belum membuktikan generalisasi ke kueri produksi.