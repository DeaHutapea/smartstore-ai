"""Test kasus ekstrem (edge case) untuk CSP solver keranjang — Milestone 2.

Fokus: nilai batas (boundary) pada budget, deadline, threshold gratis ongkir,
serta masukan degenerate (keranjang kosong, produk tanpa penjual).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from csp.cart_solver import (  # noqa: E402
    CART_CATALOG,
    FREE_SHIPPING_THRESHOLD,
    FLAT_SHIPPING_FEE,
    MAX_DELIVERY_GAP_DAYS,
    Offer,
    solve_cart,
)

OPTIMAL_COST = 4800  # biaya termurah katalog dasar (lihat test_cart_solver.py)


def test_empty_cart_costs_nothing():
    """Keranjang kosong tidak boleh crash: tidak ada yang dibeli, biaya 0."""
    result = solve_cart({}, budget=1000, deadline_days=5)
    assert result["status"] == "optimal"
    assert result["assignment"] == {}
    assert result["total_cost"] == 0


def test_product_without_any_seller_is_infeasible():
    """Produk yang tidak punya penjual membuat keranjang tidak mungkin dipenuhi."""
    result = solve_cart({"Laptop": []}, budget=10_000, deadline_days=5)
    assert result["status"] == "infeasible"
    assert "Laptop" in result["reason"]


def test_budget_exactly_at_optimum_is_feasible():
    """Batas budget bersifat inklusif (<=): budget == biaya optimal harus lolos."""
    result = solve_cart(CART_CATALOG, budget=OPTIMAL_COST, deadline_days=10)
    assert result["status"] == "optimal"
    assert result["total_cost"] == OPTIMAL_COST


def test_budget_one_below_optimum_is_infeasible():
    """Budget kurang 1 dari biaya optimal harus ditolak."""
    result = solve_cart(CART_CATALOG, budget=OPTIMAL_COST - 1, deadline_days=10)
    assert result["status"] == "infeasible"


def test_deadline_boundary_is_inclusive():
    """Deadline 2 hari: hanya MegaStore (2 hari) yang lolos, dan itu cukup."""
    result = solve_cart(CART_CATALOG, budget=99_999, deadline_days=2)
    assert result["status"] == "optimal"
    assert {o.seller for o in result["assignment"].values()} == {"MegaStore"}


def test_deadline_one_day_is_infeasible_with_clear_reason():
    result = solve_cart(CART_CATALOG, budget=99_999, deadline_days=1)
    assert result["status"] == "infeasible"
    assert "deadline" in result["reason"]


def test_delivery_gap_too_large_is_rejected_by_ac3():
    """Dua produk dengan selisih kirim > MAX_DELIVERY_GAP_DAYS tidak boleh digabung."""
    catalog = {
        "A": [Offer("S1", 10, "Jakarta", 1)],
        "B": [Offer("S2", 10, "Jakarta", 1 + MAX_DELIVERY_GAP_DAYS + 1)],
    }
    result = solve_cart(catalog, budget=1_000, deadline_days=30)
    assert result["status"] == "infeasible"
    assert "AC-3" in result["reason"]


def test_delivery_gap_exactly_at_limit_is_allowed():
    catalog = {
        "A": [Offer("S1", 10, "Jakarta", 1)],
        "B": [Offer("S2", 10, "Jakarta", 1 + MAX_DELIVERY_GAP_DAYS)],
    }
    result = solve_cart(catalog, budget=1_000, deadline_days=30)
    assert result["status"] == "optimal"


@pytest.mark.parametrize(
    "price, expected_shipping",
    [
        (FREE_SHIPPING_THRESHOLD, 0),                       # tepat di threshold -> gratis
        (FREE_SHIPPING_THRESHOLD - 1, FLAT_SHIPPING_FEE),   # 1 di bawah -> kena ongkir
    ],
)
def test_free_shipping_threshold_boundary(price, expected_shipping):
    catalog = {"Laptop": [Offer("Toko", price, "Jakarta", 2)]}
    result = solve_cart(catalog, budget=100_000, deadline_days=5)
    assert result["status"] == "optimal"
    assert result["total_cost"] == price + expected_shipping
