import sys
from pathlib import Path

# Tambahkan direktori root proyek ke sys.path agar modul 'src' dapat ditemukan
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.csp.cart_solver import solve_cart_optimization


def test_empty_cart():
    """Edge Case: Memastikan solver menangani keranjang belanja kosong secara bijak."""
    empty_items = []
    catalog = []

    result = solve_cart_optimization(empty_items, catalog)

    # Hasil harus mengembalikan struktur yang valid tanpa error/crash
    assert result is not None
    assert isinstance(result, dict)