"""
CSP Solver — Optimasi Keranjang Belanja Multi-Produk (Milestone 2)

Masalah bisnis: pelanggan punya keranjang berisi beberapa produk berbeda.
Setiap produk dijual oleh beberapa penjual dengan harga, kota gudang, dan
estimasi lama pengiriman yang berbeda-beda. Sistem harus memilih SATU
penjual untuk SETIAP produk sekaligus, sehingga:
  - Total biaya (harga produk + ongkir, dengan gratis ongkir jika belanja
    dari satu penjual melewati threshold) seminimal mungkin.
  - Semua batasan bisnis terpenuhi (budget maksimal, tenggat pengiriman,
    dan produk-produk tidak boleh datang terlalu berjauhan waktunya).

Pemodelan CSP formal:
  - Variables   : nama tiap produk di keranjang, mis. {Laptop, Mouse, Keyboard}
  - Domain      : daftar Offer (penjual, harga, kota, lama_kirim) yang
                   menjual produk tsb.
  - Constraints :
      1. Unary  (node consistency) — lama_kirim setiap opsi <= deadline
         pelanggan. Opsi yang melanggar dibuang lebih dulu (node consistency,
         bagian dari propagasi batasan sebelum pencarian).
      2. Binary (AC-3)             — untuk setiap pasangan produk (Xi, Xj),
         selisih lama_kirim opsi yang dipilih <= MAX_DELIVERY_GAP_DAYS (semua
         produk harus tiba dalam rentang waktu berdekatan, tidak terpisah
         jauh).
      3. Global (dicek saat backtracking, bukan arc) — total biaya (dengan
         aturan gratis ongkir per penjual) <= budget pelanggan.

Algoritma: AC-3 (reduksi domain) -> Backtracking Search dengan heuristik
MRV (Minimum Remaining Values) untuk pilih variabel, dan LCV (Least
Constraining Value, di sini: harga termurah dulu) untuk urutan opsi, plus
forward checking & branch-and-bound pruning terhadap budget.
"""

from __future__ import annotations

import math
import statistics
import time
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# 1. Data: katalog penjual per produk (data dummy realistis)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Offer:
    seller: str
    price: int          # ribuan Rupiah
    city: str
    delivery_days: int  # estimasi lama pengiriman (hari)


CART_CATALOG: dict[str, list[Offer]] = {
    "Laptop": [
        Offer("TokoAndi", 4500, "Jakarta", 3),
        Offer("GadgetPro", 4350, "Semarang", 5),
        Offer("MegaStore", 4600, "Surabaya", 2),
    ],
    "Mouse": [
        Offer("TokoAndi", 150, "Jakarta", 3),
        Offer("BudiElektronik", 130, "Yogyakarta", 4),
        Offer("MegaStore", 160, "Surabaya", 2),
    ],
    "Keyboard": [
        Offer("GadgetPro", 300, "Semarang", 5),
        Offer("BudiElektronik", 280, "Yogyakarta", 4),
        Offer("MegaStore", 320, "Surabaya", 2),
    ],
}

FREE_SHIPPING_THRESHOLD = 4700   # ribu Rupiah, belanja per penjual >= ini -> gratis ongkir
FLAT_SHIPPING_FEE = 20           # ribu Rupiah, kalau di bawah threshold
MAX_DELIVERY_GAP_DAYS = 2        # selisih maksimal lama kirim antar produk


# ---------------------------------------------------------------------------
# 2. Node consistency (unary constraint) + AC-3 (binary constraint)
# ---------------------------------------------------------------------------

def apply_node_consistency(domains: dict[str, list[Offer]], deadline_days: int) -> dict[str, list[Offer]]:
    """Buang opsi yang lama kirimnya melebihi deadline pelanggan."""
    return {item: [o for o in offers if o.delivery_days <= deadline_days] for item, offers in domains.items()}


def satisfies_binary(a: Offer, b: Offer) -> bool:
    """Batasan biner: selisih lama kirim dua opsi <= MAX_DELIVERY_GAP_DAYS."""
    return abs(a.delivery_days - b.delivery_days) <= MAX_DELIVERY_GAP_DAYS


def revise(domains: dict[str, list[Offer]], xi: str, xj: str) -> bool:
    """Buang nilai di domain(xi) yang tidak punya pasangan valid di domain(xj)."""
    revised = False
    kept = []
    for oi in domains[xi]:
        if any(satisfies_binary(oi, oj) for oj in domains[xj]):
            kept.append(oi)
        else:
            revised = True
    domains[xi] = kept
    return revised


def ac3(domains: dict[str, list[Offer]], variables: list[str]) -> bool:
    """AC-3: propagasi batasan biner sampai arc-consistent, atau domain
    kosong (berarti CSP tidak punya solusi valid)."""
    queue = [(xi, xj) for xi in variables for xj in variables if xi != xj]
    while queue:
        xi, xj = queue.pop(0)
        if revise(domains, xi, xj):
            if not domains[xi]:
                return False
            for xk in variables:
                if xk not in (xi, xj):
                    queue.append((xk, xi))
    return True


# ---------------------------------------------------------------------------
# 3. Fungsi biaya (dengan aturan gratis ongkir per penjual)
# ---------------------------------------------------------------------------

def compute_total_cost(assignment: dict[str, Offer]) -> int:
    total_price = sum(o.price for o in assignment.values())
    spend_per_seller: dict[str, int] = {}
    for o in assignment.values():
        spend_per_seller[o.seller] = spend_per_seller.get(o.seller, 0) + o.price

    shipping = 0
    counted: set[str] = set()
    for o in assignment.values():
        if o.seller in counted:
            continue
        counted.add(o.seller)
        if spend_per_seller[o.seller] < FREE_SHIPPING_THRESHOLD:
            shipping += FLAT_SHIPPING_FEE

    return total_price + shipping


# ---------------------------------------------------------------------------
# 4. Backtracking Search dengan MRV + LCV + forward checking + branch&bound
# ---------------------------------------------------------------------------

def select_unassigned_variable(domains: dict[str, list[Offer]], assignment: dict[str, Offer]) -> str:
    """MRV: pilih variabel belum terisi dengan domain tersisa TERKECIL."""
    unassigned = [v for v in domains if v not in assignment]
    return min(unassigned, key=lambda v: len(domains[v]))


def order_domain_values(
    var: str,
    domains: dict[str, list[Offer]],
    assignment: dict[str, Offer],
) -> list[Offer]:
    """LCV: try offers that preserve the most compatible remaining values."""
    unassigned = [item for item in domains if item != var and item not in assignment]

    def score(offer: Offer) -> tuple[int, int]:
        remaining_values = sum(
            satisfies_binary(offer, other_offer)
            for item in unassigned
            for other_offer in domains[item]
        )
        return -remaining_values, offer.price

    return sorted(domains[var], key=score)


def backtracking_search(
    domains: dict[str, list[Offer]], variables: list[str], budget: int
) -> tuple[dict[str, Offer] | None, float, int]:
    """Mengembalikan (assignment_termurah, biaya_termurah, jumlah_node_dikunjungi)."""
    best_assignment: dict[str, Offer] | None = None
    best_cost = math.inf
    nodes_visited = 0

    def backtrack(assignment: dict[str, Offer], domains: dict[str, list[Offer]]) -> None:
        nonlocal best_assignment, best_cost, nodes_visited
        nodes_visited += 1

        if len(assignment) == len(variables):
            cost = compute_total_cost(assignment)
            if cost <= budget and cost < best_cost:
                best_assignment = dict(assignment)
                best_cost = cost
            return

        # Lower-bound the final price by adding the cheapest remaining offer
        # for each unassigned product. Shipping is non-negative, so this is
        # also a lower bound on the final cost.
        partial_price = sum(o.price for o in assignment.values())
        unassigned = [item for item in variables if item not in assignment]
        cheapest_remaining = sum(min(o.price for o in domains[item]) for item in unassigned)
        spend_per_seller: dict[str, int] = {}
        for offer in assignment.values():
            spend_per_seller[offer.seller] = spend_per_seller.get(offer.seller, 0) + offer.price

        unavoidable_shipping = 0
        for seller, spend in spend_per_seller.items():
            if spend >= FREE_SHIPPING_THRESHOLD:
                continue
            maximum_future_spend = sum(
                max(
                    (offer.price for offer in domains[item] if offer.seller == seller),
                    default=0,
                )
                for item in unassigned
            )
            if spend + maximum_future_spend < FREE_SHIPPING_THRESHOLD:
                unavoidable_shipping += FLAT_SHIPPING_FEE

        minimum_possible_cost = partial_price + cheapest_remaining + unavoidable_shipping
        if minimum_possible_cost > budget or minimum_possible_cost >= best_cost:
            return

        var = select_unassigned_variable(domains, assignment)
        for offer in order_domain_values(var, domains, assignment):
            assignment[var] = offer

            # Forward checking: filter domain variabel lain sesuai batasan biner.
            new_domains = {item: offers.copy() for item, offers in domains.items()}
            new_domains[var] = [offer]
            consistent = True
            for other in variables:
                if other == var or other in assignment:
                    continue
                new_domains[other] = [o for o in new_domains[other] if satisfies_binary(offer, o)]
                if not new_domains[other]:
                    consistent = False
                    break

            if consistent:
                backtrack(assignment, new_domains)

            del assignment[var]

    backtrack({}, domains)
    return best_assignment, best_cost, nodes_visited


# ---------------------------------------------------------------------------
# 5. Fungsi utama: jalankan solver end-to-end untuk satu skenario
# ---------------------------------------------------------------------------

def solve_cart(
    catalog: dict[str, list[Offer]], budget: int, deadline_days: int
) -> dict:
    variables = list(catalog.keys())
    domains = apply_node_consistency(catalog, deadline_days)

    for item in variables:
        if not domains[item]:
            return {"status": "infeasible", "reason": f"Tidak ada penjual '{item}' yang memenuhi deadline {deadline_days} hari"}

    if not ac3(domains, variables):
        return {"status": "infeasible", "reason": "AC-3: tidak ada kombinasi yang memenuhi batasan selisih waktu kirim antar produk"}

    assignment, cost, nodes = backtracking_search(domains, variables, budget)
    if assignment is None:
        return {"status": "infeasible", "reason": f"Tidak ada kombinasi penjual dengan total biaya <= budget Rp {budget} ribu"}

    return {
        "status": "optimal",
        "assignment": assignment,
        "total_cost": cost,
        "nodes_visited": nodes,
    }


# ---------------------------------------------------------------------------
# 6. Demo
# ---------------------------------------------------------------------------

def print_result(result: dict) -> None:
    if result["status"] == "infeasible":
        print(f"  STATUS: INFEASIBLE — {result['reason']}")
        return
    print(f"  STATUS: OPTIMAL (node dikunjungi: {result['nodes_visited']})")
    for item, offer in result["assignment"].items():
        print(f"    - {item}: beli dari {offer.seller} (Rp {offer.price} ribu, {offer.city}, {offer.delivery_days} hari)")
    print(f"  Total biaya (harga + ongkir): Rp {result['total_cost']} ribu")


def main() -> None:
    print("=== Skenario 1: budget cukup, deadline longgar ===")
    print_result(solve_cart(CART_CATALOG, budget=5200, deadline_days=6))

    print("\n=== Skenario 2: budget ketat ===")
    print_result(solve_cart(CART_CATALOG, budget=4800, deadline_days=6))

    print("\n=== Skenario 3: deadline sangat ketat (infeasible) ===")
    print_result(solve_cart(CART_CATALOG, budget=5200, deadline_days=1))

    print("\n=== Analisis Sensitivitas: waktu vs ukuran masalah ===")
    for n_extra in [0, 3, 6, 9]:
        big_catalog = dict(CART_CATALOG)
        # Perbesar masalah dengan menambah produk dummy bervariasi seller
        for i in range(n_extra):
            big_catalog[f"Produk{i}"] = [
                Offer(f"Seller{i}A", 100 + i, "Jakarta", 2),
                Offer(f"Seller{i}B", 90 + i, "Semarang", 4),
                Offer(f"Seller{i}C", 110 + i, "Surabaya", 3),
            ]
        run_times = []
        run_results = []
        for _ in range(5):
            start = time.perf_counter()
            run_results.append(solve_cart(big_catalog, budget=20000, deadline_days=10))
            run_times.append(time.perf_counter() - start)
        elapsed = statistics.median(run_times)
        n_vars = len(big_catalog)
        result = run_results[-1]
        nodes = result.get("nodes_visited", "-")
        print(
            f"  {n_vars} produk -> median 5 run: {elapsed * 1000:.2f} ms, "
            f"node dikunjungi: {nodes}"
        )


if __name__ == "__main__":
    main()
