from itertools import product
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from csp.cart_solver import (  # noqa: E402
    CART_CATALOG,
    apply_node_consistency,
    compute_total_cost,
    satisfies_binary,
    solve_cart,
)


def test_finds_optimal_within_budget():
    result = solve_cart(CART_CATALOG, budget=5200, deadline_days=6)
    assert result["status"] == "optimal"
    assert result["total_cost"] <= 5200


def test_tight_deadline_is_infeasible():
    # Tidak ada penjual dengan lama kirim <= 1 hari untuk produk apa pun.
    result = solve_cart(CART_CATALOG, budget=999999, deadline_days=1)
    assert result["status"] == "infeasible"


def test_tiny_budget_is_infeasible():
    result = solve_cart(CART_CATALOG, budget=10, deadline_days=10)
    assert result["status"] == "infeasible"


def test_optimal_cost_is_deterministic_minimum():
    # Solusi termurah untuk skenario dasar harus konsisten = 4800
    # (GadgetPro Laptop 4350 + BudiElektronik Mouse 130 + BudiElektronik
    # Keyboard 280 + 20 ongkir GadgetPro + 20 ongkir BudiElektronik).
    result = solve_cart(CART_CATALOG, budget=999999, deadline_days=10)
    assert result["status"] == "optimal"
    assert result["total_cost"] == 4800


def test_solver_matches_brute_force_for_small_catalog():
    budget = 5200
    deadline_days = 6
    domains = apply_node_consistency(CART_CATALOG, deadline_days)
    assignments = product(*(domains[item] for item in CART_CATALOG))
    feasible_costs = [
        compute_total_cost(dict(zip(CART_CATALOG, offers)))
        for offers in assignments
        if all(
            satisfies_binary(offers[i], offers[j])
            for i in range(len(offers))
            for j in range(i + 1, len(offers))
        )
    ]
    expected_cost = min(cost for cost in feasible_costs if cost <= budget)

    result = solve_cart(CART_CATALOG, budget=budget, deadline_days=deadline_days)

    assert result["status"] == "optimal"
    assert result["total_cost"] == expected_cost
