# Benchmark `kb_paraphrase_multilingual_minilm_l12_v2_c80_o16`

Model: `paraphrase-multilingual-MiniLM-L12-v2` · chunk=80 kata · overlap=16 · 688 chunk

| Tipe | n | Hit@1 | Hit@3 | MRR | Rata-rata skor top-1 |
|---|---|---|---|---|---|
| synonym | 8 | 0.75 | 0.88 | 0.84 | 0.686 |
| ambiguous | 3 | 0.33 | 0.67 | 0.50 | 0.705 |
| out_of_domain | 5 | – | – | – | 0.230 |

**Ambang OOD (kalibrasi, balanced accuracy=1.00): 0.439** — in-domain diterima 11/11, out-of-domain ditolak 5/5.

| ID | Tipe | Kueri | Top-1 | Skor | Ekspektasi | Rank |
|---|---|---|---|---|---|---|
| Q01 | synonym | Berapa lama uang saya kembali setelah pesanan dibatalkan? | MKT006 | 0.6663 | MKT004 | 4 |
| Q02 | synonym | Kenapa paket saya telat sampai melebihi perkiraan? | MKT001 | 0.604 | MKT001 | 1 |
| Q03 | synonym | Penjual menolak keluhan saya, langkah apa yang bisa saya tempuh? | MKT002 | 0.6144 | MKT002 | 1 |
| Q04 | synonym | Voucher bebas biaya kirim bisa dipakai di jenis toko apa saja? | MKT003 | 0.5364 | MKT003,MKT008 | 1 |
| Q05 | synonym | Apa hak pembeli jika barang yang diterima tidak sesuai perjanjian? | MKT007 | 0.8042 | REG001 | 2 |
| Q06 | synonym | Kewajiban penyelenggara platform dalam menjaga kerahasiaan data pribadi pengguna | REG003 | 0.7575 | REG003 | 1 |
| Q07 | synonym | Berapa hari batas waktu retur barang di Shopee Mall? | MKT006 | 0.8297 | MKT005,MKT006 | 1 |
| Q08 | synonym | Kewajiban pelaku usaha yang berdagang lewat sistem elektronik | REG002 | 0.6792 | REG002 | 1 |
| Q09 | ambiguous | Bagaimana kebijakan pengembalian? | MKT005 | 0.6983 | MKT004,MKT005,MKT007 | 1 |
| Q10 | ambiguous | Aturan soal pengiriman barang | REG002 | 0.7528 | MKT001,MKT003,REG004 | 2 |
| Q11 | ambiguous | Syarat dan ketentuan | REG001 | 0.6636 | MKT007,MKT008 | – |
| Q12 | out_of_domain | Resep nasi goreng seafood yang enak | REG001 | 0.1976 | – | – |
| Q13 | out_of_domain | Siapa juara Liga Champions musim lalu? | REG001 | 0.2228 | – | – |
| Q14 | out_of_domain | Cara install Python di Windows 11 | REG004 | 0.1554 | – | – |
| Q15 | out_of_domain | Prakiraan cuaca besok di Medan | REG004 | 0.3415 | – | – |
| Q16 | out_of_domain | Apa itu teori relativitas Einstein? | REG003 | 0.232 | – | – |