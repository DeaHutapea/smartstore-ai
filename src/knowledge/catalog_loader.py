"""Loader katalog penjual dari berkas JSON (Data & Knowledge Layer).

Memisahkan DATA dari LOGIKA: solver di ``csp/cart_solver.py`` tetap menerima
``dict[str, list[Offer]]``, sehingga data dummy bisa diganti data nyata
(mis. hasil scraping) cukup dengan menormalisasinya ke format JSON ini.

Validasi dilakukan di sini agar data rusak gagal dengan pesan jelas, bukan
menghasilkan solusi yang salah diam-diam di dalam solver.
"""

from __future__ import annotations

import json
from pathlib import Path

from csp.cart_solver import Offer

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "cart_catalog.json"

_REQUIRED_FIELDS = ("seller", "price", "city", "delivery_days")


def _parse_offer(product: str, raw: dict) -> Offer:
    missing = [f for f in _REQUIRED_FIELDS if f not in raw]
    if missing:
        raise ValueError(f"Produk '{product}': field wajib hilang: {', '.join(missing)}")

    price, days = raw["price"], raw["delivery_days"]
    if isinstance(price, bool) or not isinstance(price, int) or price <= 0:
        raise ValueError(f"Produk '{product}', penjual '{raw['seller']}': price harus bilangan bulat > 0")
    if isinstance(days, bool) or not isinstance(days, int) or days < 0:
        raise ValueError(f"Produk '{product}', penjual '{raw['seller']}': delivery_days harus bilangan bulat >= 0")
    if not str(raw["seller"]).strip() or not str(raw["city"]).strip():
        raise ValueError(f"Produk '{product}': seller dan city tidak boleh kosong")

    return Offer(seller=raw["seller"], price=price, city=raw["city"], delivery_days=days)


def load_cart_catalog(path: str | Path | None = None) -> dict[str, list[Offer]]:
    """Baca katalog dari JSON dan kembalikan dalam format yang dipakai solver."""
    source = Path(path) if path is not None else DEFAULT_CATALOG_PATH
    with source.open(encoding="utf-8") as f:
        payload = json.load(f)

    if "catalog" not in payload or not isinstance(payload["catalog"], dict):
        raise ValueError("Berkas katalog harus memiliki objek 'catalog'")

    return {
        product: [_parse_offer(product, raw) for raw in offers]
        for product, offers in payload["catalog"].items()
    }


if __name__ == "__main__":
    for product, offers in load_cart_catalog().items():
        print(f"{product}: {len(offers)} penjual")
