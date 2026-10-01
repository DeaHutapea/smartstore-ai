# Skema Data Katalog — SmartStore AI

Dokumen ini menjelaskan struktur data yang dipakai solver CSP (Milestone 2)
dan rencana penggantian data dummy dengan data nyata.

## Berkas
- `data/cart_catalog.json` — katalog penjual per produk.
- `src/knowledge/catalog_loader.py` — membaca, memvalidasi, dan mengubah JSON
  menjadi `dict[str, list[Offer]]` yang dipakai `csp/cart_solver.py`.

## Struktur `cart_catalog.json`
```json
{
  "_meta": { "unit_price": "ribuan Rupiah", "unit_delivery": "hari", "note": "..." },
  "catalog": {
    "<nama produk>": [
      {"seller": "...", "price": 4500, "city": "Jakarta", "delivery_days": 3}
    ]
  }
}
```

| Field | Tipe | Aturan validasi | Keterangan |
|---|---|---|---|
| `seller` | string | tidak kosong | Nama penjual |
| `price` | integer | > 0 | Harga produk, **ribuan Rupiah** (4500 = Rp4.500.000) |
| `city` | string | tidak kosong | Kota gudang penjual |
| `delivery_days` | integer | >= 0 | Estimasi lama pengiriman, hari |

Satu kunci di `catalog` = satu **variabel** CSP; daftar penawarannya = **domain**.

## Aturan bisnis yang TIDAK ada di JSON
Konstanta berikut masih di `cart_solver.py`: `FREE_SHIPPING_THRESHOLD` (4700),
`FLAT_SHIPPING_FEE` (20), dan `MAX_DELIVERY_GAP_DAYS` (2). Budget dan deadline
adalah input pelanggan saat `solve_cart(...)` dipanggil.

## Status & keterbatasan data
- Seluruh data saat ini **simulasi**, bukan hasil scraping marketplace.
- Data tidak memuat data pribadi (hanya nama toko fiktif, harga, kota gudang).
- Kesimpulan eksperimen hanya berlaku untuk katalog contoh ini.

## Rencana Milestone 3
Data nyata dinormalisasi ke format JSON yang sama (harga ke ribuan Rupiah,
lama kirim ke hari), lalu divalidasi oleh loader sebelum dipakai solver.
