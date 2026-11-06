# Benchmark `kb_multilingual_e5_small_c120_o24`

Model: `intfloat/multilingual-e5-small` · chunk=120 kata · overlap=24 · 449 chunk

| Tipe | n | Hit@1 | Hit@3 | MRR | Rata-rata skor top-1 |
|---|---|---|---|---|---|
| synonym | 8 | 0.75 | 0.88 | 0.83 | 0.877 |
| ambiguous | 3 | 0.67 | 0.67 | 0.73 | 0.877 |
| out_of_domain | 5 | – | – | – | 0.789 |

**Ambang OOD (kalibrasi, balanced accuracy=1.00): 0.838** — in-domain diterima 11/11, out-of-domain ditolak 5/5.

| ID | Tipe | Kueri | Top-1 | Skor | Ekspektasi | Rank |
|---|---|---|---|---|---|---|
| Q01 | synonym | Berapa lama uang saya kembali setelah pesanan dibatalkan? | REG004 | 0.8603 | MKT004 | 6 |
| Q02 | synonym | Kenapa paket saya telat sampai melebihi perkiraan? | MKT001 | 0.8601 | MKT001 | 1 |
| Q03 | synonym | Penjual menolak keluhan saya, langkah apa yang bisa saya tempuh? | MKT002 | 0.8732 | MKT002 | 1 |
| Q04 | synonym | Voucher bebas biaya kirim bisa dipakai di jenis toko apa saja? | MKT008 | 0.8712 | MKT003,MKT008 | 1 |
| Q05 | synonym | Apa hak pembeli jika barang yang diterima tidak sesuai perjanjian? | REG001 | 0.866 | REG001 | 1 |
| Q06 | synonym | Kewajiban penyelenggara platform dalam menjaga kerahasiaan data pribadi pengguna | REG004 | 0.9028 | REG003 | 2 |
| Q07 | synonym | Berapa hari batas waktu retur barang di Shopee Mall? | MKT006 | 0.8985 | MKT005,MKT006 | 1 |
| Q08 | synonym | Kewajiban pelaku usaha yang berdagang lewat sistem elektronik | REG002 | 0.8877 | REG002 | 1 |
| Q09 | ambiguous | Bagaimana kebijakan pengembalian? | MKT005 | 0.8787 | MKT004,MKT005,MKT007 | 1 |
| Q10 | ambiguous | Aturan soal pengiriman barang | REG002 | 0.8899 | MKT001,MKT003,REG004 | 5 |
| Q11 | ambiguous | Syarat dan ketentuan | MKT008 | 0.8616 | MKT007,MKT008 | 1 |
| Q12 | out_of_domain | Resep nasi goreng seafood yang enak | MKT004 | 0.8073 | – | – |
| Q13 | out_of_domain | Siapa juara Liga Champions musim lalu? | REG004 | 0.7632 | – | – |
| Q14 | out_of_domain | Cara install Python di Windows 11 | MKT004 | 0.7891 | – | – |
| Q15 | out_of_domain | Prakiraan cuaca besok di Medan | REG004 | 0.8166 | – | – |
| Q16 | out_of_domain | Apa itu teori relativitas Einstein? | REG003 | 0.767 | – | – |