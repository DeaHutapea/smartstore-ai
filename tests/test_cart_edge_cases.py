import pytest
from src.csp.cart_solver import solve_cart

class DummyOffer:
    def __init__(self, id, price, seller, shipping, delivery_days):
        self.id = id
        self.price = price
        self.seller = seller
        self.shipping = shipping
        self.delivery_days = delivery_days

def test_insufficient_budget():
    """Uji skenario anggaran terlalu kecil (Zero/Insufficient Budget)."""
    catalog = {
        "item1": [
            DummyOffer("offer1", 50000, "Toko A", 10000, 2)
        ]
    }
    budget = 10000  # Anggaran di bawah harga termurah
    result = solve_cart(catalog, budget=budget, deadline_days=3)
    assert result is not None

def test_empty_catalog():
    """Uji skenario katalog produk kosong (Empty Catalog Input)."""
    catalog = {}
    budget = 100000
    result = solve_cart(catalog, budget=budget, deadline_days=3)
    assert result is not None

def test_exact_budget_fit():
    """Uji skenario anggaran pas dengan harga item (Exact Budget Fit)."""
    catalog = {
        "item1": [
            DummyOffer("offer2", 5000, "Toko B", 0, 1)
        ]
    }
    budget = 5000
    result = solve_cart(catalog, budget=budget, deadline_days=3)
    assert result is not None