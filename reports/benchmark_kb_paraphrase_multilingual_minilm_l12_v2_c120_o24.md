# Benchmark `kb_paraphrase_multilingual_minilm_l12_v2_c120_o24`

Model: `paraphrase-multilingual-MiniLM-L12-v2` · chunk=120 kata · overlap=24 · 449 chunk

| Tipe | n | Hit@1 | Hit@3 | MRR | Rata-rata skor top-1 |
|---|---|---|---|---|---|
| synonym | 8 | 0.75 | 0.88 | 0.84 | 0.681 |
| ambiguous | 3 | 0.33 | 0.67 | 0.57 | 0.702 |
| out_of_domain | 5 | – | – | – | 0.209 |

**Ambang OOD (kalibrasi, balanced accuracy=1.00): 0.423** — in-domain diterima 11/11, out-of-domain ditolak 5/5.

| ID | Tipe | Kueri | Top-1 | Skor | Ekspektasi | Rank |
|---|---|---|---|---|---|---|
| Q01 | synonym | Berapa lama uang saya kembali setelah pesanan dibatalkan? | MKT006 | 0.6765 | MKT004 | 4 |
| Q02 | synonym | Kenapa paket saya telat sampai melebihi perkiraan? | MKT001 | 0.6221 | MKT001 | 1 |
| Q03 | synonym | Penjual menolak keluhan saya, langkah apa yang bisa saya tempuh? | MKT002 | 0.621 | MKT002 | 1 |
| Q04 | synonym | Voucher bebas biaya kirim bisa dipakai di jenis toko apa saja? | MKT008 | 0.5375 | MKT003,MKT008 | 1 |
| Q05 | synonym | Apa hak pembeli jika barang yang diterima tidak sesuai perjanjian? | MKT007 | 0.7807 | REG001 | 2 |
| Q06 | synonym | Kewajiban penyelenggara platform dalam menjaga kerahasiaan data pribadi pengguna | REG003 | 0.7158 | REG003 | 1 |
| Q07 | synonym | Berapa hari batas waktu retur barang di Shopee Mall? | MKT006 | 0.8344 | MKT005,MKT006 | 1 |
| Q08 | synonym | Kewajiban pelaku usaha yang berdagang lewat sistem elektronik | REG002 | 0.6582 | REG002 | 1 |
| Q09 | ambiguous | Bagaimana kebijakan pengembalian? | MKT005 | 0.7109 | MKT004,MKT005,MKT007 | 1 |
| Q10 | ambiguous | Aturan soal pengiriman barang | REG002 | 0.7538 | MKT001,MKT003,REG004 | 2 |
| Q11 | ambiguous | Syarat dan ketentuan | REG004 | 0.6424 | MKT007,MKT008 | 5 |
| Q12 | out_of_domain | Resep nasi goreng seafood yang enak | REG001 | 0.1754 | – | – |
| Q13 | out_of_domain | Siapa juara Liga Champions musim lalu? | REG001 | 0.2166 | – | – |
| Q14 | out_of_domain | Cara install Python di Windows 11 | MKT008 | 0.131 | – | – |
| Q15 | out_of_domain | Prakiraan cuaca besok di Medan | REG004 | 0.3083 | – | – |
| Q16 | out_of_domain | Apa itu teori relativitas Einstein? | REG003 | 0.212 | – | – |