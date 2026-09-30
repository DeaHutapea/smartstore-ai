import heapq
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from search.price_search import (  # noqa: E402
    CITY_COORDS,
    DISTRIBUTION_EDGES,
    SELLERS,
    START,
    a_star_search,
    heuristic,
    uniform_cost_search,
)


def test_ucs_finds_cheapest_total_price():
    path, cost, _ = uniform_cost_search("Malang")
    assert path[0] == "START"
    assert cost == 267  # GadgetPro (235) + Semarang->Surabaya (22) + Surabaya->Malang (10)


def test_astar_matches_ucs_cost():
    _, cost_ucs, _ = uniform_cost_search("Malang")
    _, cost_astar, _ = a_star_search("Malang")
    assert math.isclose(cost_ucs, cost_astar)


def test_astar_expands_fewer_or_equal_nodes():
    _, _, expanded_ucs = uniform_cost_search("Malang")
    _, _, expanded_astar = a_star_search("Malang")
    assert expanded_astar <= expanded_ucs


def test_goal_at_seller_own_city():
    # Jakarta punya penjual sendiri (TokoAndi) -> harusnya harga = harga
    # produk saja (ongkir 0, karena goal == kota gudang penjual itu).
    path, cost, _ = uniform_cost_search("Jakarta")
    assert cost == 250


def test_astar_heuristic_is_admissible_for_every_city_pair():
    cities = list(CITY_COORDS)
    for source in cities:
        distances = {city: math.inf for city in cities}
        distances[source] = 0
        frontier = [(0, source)]

        while frontier:
            cost, city = heapq.heappop(frontier)
            if cost != distances[city]:
                continue
            for neighbor, edge_cost in DISTRIBUTION_EDGES[city].items():
                candidate = cost + edge_cost
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    heapq.heappush(frontier, (candidate, neighbor))

        for goal in cities:
            assert heuristic(source, goal) <= distances[goal]

    for city, neighbors in DISTRIBUTION_EDGES.items():
        for neighbor, edge_cost in neighbors.items():
            assert heuristic(city, "Malang") <= edge_cost + heuristic(neighbor, "Malang")

    for seller, info in SELLERS.items():
        assert heuristic(START, "Malang") <= info["price"] + heuristic(seller, "Malang")

    assert heuristic(START, "Malang") == 0
