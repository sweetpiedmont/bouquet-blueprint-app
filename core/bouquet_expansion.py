def bouquet_cost(
    allocation: dict[str, int],
    avg_wholesale_prices: dict[str, float],
) -> float:
    return sum(
        allocation[c] * avg_wholesale_prices[c]
        for c in allocation
    )

def can_add_stem(
    allocation: dict[str, int],
    category: str,
    stem_bounds: dict[str, dict[str, float]],
    available_stems: dict[str, int],
    max_bouquets: int,
) -> bool:
    """
    Check whether adding 1 stem to a category is legal.
    """

    current = allocation.get(category, 0)
    bounds = stem_bounds[category]

    # Must not exceed absolute max
    if current + 1 > bounds["absolute_max"]:
        return False

    # Must have enough available stems to support all bouquets
    required_total = (current + 1) * max_bouquets
    if available_stems.get(category, 0) < required_total:
        return False

    return True

def score_addition(
    allocation: dict[str, int],
    category: str,
    stem_bounds: dict[str, dict[str, float]],
    available_stems: dict[str, int],
) -> float:
    """
    Higher score = better candidate for adding a stem.
    """

    current = allocation[category]
    bounds = stem_bounds[category]

    # Distance from design target (prefer closer)
    design_mid = (bounds["design_min"] + bounds["design_max"]) / 2
    distance_penalty = abs((current + 1) - design_mid)

    # Availability pressure (prefer abundant stems)
    availability = available_stems.get(category, 0)

    return availability - distance_penalty * 10

def expand_bouquet_to_target(
    base_allocation: dict[str, int],
    max_bouquets: int,
    stem_bounds: dict[str, dict[str, float]],
    available_stems: dict[str, int],
    avg_wholesale_prices: dict[str, float],
    target_price: float,
) -> dict[str, int]:
    """
    Expand a bouquet by adding stems until target price is met
    or no further legal additions are possible.
    """

    allocation = base_allocation.copy()

    # ---- expansion loop (price-driven) ----
    while bouquet_cost(allocation, avg_wholesale_prices) < target_price:
        candidates = []

        for category in allocation.keys():
            if can_add_stem(
                allocation,
                category,
                stem_bounds,
                available_stems,
                max_bouquets,
            ):
                score = score_addition(
                    allocation,
                    category,
                    stem_bounds,
                    available_stems,
                )
                candidates.append((score, category))

        if not candidates:
            break  # cannot add more legally

        _, chosen = max(candidates)
        allocation[chosen] += 1

    return allocation
