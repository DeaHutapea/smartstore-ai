import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from csp.cart_solver import CART_CATALOG, solve_cart  # noqa: E402
from knowledge.catalog_loader import load_cart_catalog  # noqa: E402


def _write(tmp_path, payload) -> Path:
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_json_catalog_matches_builtin_catalog():
    """Data JSON harus identik dengan katalog bawaan di cart_solver.py."""
    assert load_cart_catalog() == CART_CATALOG


def test_solver_gives_same_result_with_loaded_catalog():
    loaded = solve_cart(load_cart_catalog(), budget=999_999, deadline_days=10)
    builtin = solve_cart(CART_CATALOG, budget=999_999, deadline_days=10)
    assert loaded["total_cost"] == builtin["total_cost"] == 4800


def test_missing_field_is_rejected(tmp_path):
    path = _write(tmp_path, {"catalog": {"Mouse": [{"seller": "A", "price": 100, "city": "Jakarta"}]}})
    with pytest.raises(ValueError, match="delivery_days"):
        load_cart_catalog(path)


@pytest.mark.parametrize("bad_price", [0, -5, "100", 12.5, True])
def test_invalid_price_is_rejected(tmp_path, bad_price):
    offer = {"seller": "A", "price": bad_price, "city": "Jakarta", "delivery_days": 2}
    path = _write(tmp_path, {"catalog": {"Mouse": [offer]}})
    with pytest.raises(ValueError, match="price"):
        load_cart_catalog(path)


def test_negative_delivery_days_is_rejected(tmp_path):
    offer = {"seller": "A", "price": 100, "city": "Jakarta", "delivery_days": -1}
    path = _write(tmp_path, {"catalog": {"Mouse": [offer]}})
    with pytest.raises(ValueError, match="delivery_days"):
        load_cart_catalog(path)


def test_missing_catalog_object_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="catalog"):
        load_cart_catalog(_write(tmp_path, {"produk": {}}))
