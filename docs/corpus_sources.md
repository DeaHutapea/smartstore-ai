# Provenance dan distribusi korpus

## Status sumber

| ID | Sumber | URL | Akses/status |
|---|---|---|---|
| REG001 | UU No. 8 Tahun 1999 | https://peraturan.go.id/id/uu-no-8-tahun-1999 | Status "Berlaku" pada portal resmi, dicek 2026-11-06 |
| REG002 | PP No. 80 Tahun 2019 | https://peraturan.go.id/id/pp-no-80-tahun-2019 | Status "Berlaku" pada portal resmi, dicek 2026-11-06 |
| REG003 | UU No. 27 Tahun 2022 | https://peraturan.go.id/id/uu-no-27-tahun-2022 | Status "Berlaku" pada portal resmi, dicek 2026-11-06; sebagian norma memiliki pemaknaan bersyarat oleh MK |
| REG004 | Permenkomdigi No. 8 Tahun 2025, Layanan Pos Komersial | https://peraturan.go.id/id/permenkomdigi-no-8-tahun-2025 | Status "Berlaku" pada portal resmi, dicek 2026-11-06 |
| MKT001–MKT004 | Snapshot artikel Tokopedia Care | URL dan tanggal snapshot tercatat di manifest dan front matter sumber lokal | Snapshot tercatat 2026-11-06; kebijakan dapat berubah |
| MKT005–MKT007 | Snapshot kebijakan Shopee | https://help.shopee.co.id/portal/4/category/17638-Kebijakan/418-Kebijakan-Shopee | Snapshot PDF dibuat 2026-11-06; URL kategori tercatat sebagai tautan internal, bukan URL artikel utama |
| MKT008 | S&K Gratis Ongkir Dilayani Tokopedia | https://www.tokopedia.com/help/article/syarat-dan-ketentuan-gratis-ongkir | URL dari tautan internal PDF; snapshot 2026-11-06, program mungkin historis |

Tiga PDF marketplace tambahan pada salinan kerja tidak tercantum di manifest
dan tidak masuk indeks. Keputusan ini disengaja sampai provenance, relevansi,
dan izin penggunaannya ditentukan.

## Kebijakan distribusi

PDF/teks marketplace dan hasil ekstraksi lokal dikecualikan dari Git karena
izin redistribusinya belum dibuktikan. `.gitignore` mengecualikan
`data/corpus/marketplace/` dan `data/processed/`. File lokal yang sudah ada
tidak dihapus; untuk mereproduksi indeks pada clone baru, letakkan sumber yang
boleh digunakan di struktur folder sesuai manifest dan cocokkan nama file.
Jangan mengunduh atau menyalin ulang isi tanpa memeriksa ketentuan sumber.

File regulasi di `data/corpus/regulations/` merupakan salinan kerja. Portal
resmi di atas adalah rujukan status dan sumber utama; jika salinan tidak ada,
peroleh salinan dari portal resmi dan verifikasi kecocokan sebelum membangun
indeks.

Status `berlaku` di manifest hanya diberikan pada regulasi yang dicek di
portal resmi pada tanggal di atas; ia bukan nasihat hukum dan harus diperiksa
ulang sebelum penggunaan nyata.
