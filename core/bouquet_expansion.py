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

    PRICE_TOLERANCE = 1.0
    MAX_EXPANSION_STEPS = 25
    steps = 0

    best_allocation = allocation.copy()
    best_delta = abs(bouquet_cost(allocation, avg_wholesale_prices) - target_price)

     # ---- expansion loop (price-driven) ----
    while True:
        steps += 1
        if steps > MAX_EXPANSION_STEPS:
            break

        current_cost = bouquet_cost(allocation, avg_wholesale_prices)
        current_delta = current_cost - target_price

        # If we're within tolerance, we're done
        if abs(current_delta) <= PRICE_TOLERANCE:
            best_allocation = allocation.copy()
            break

        # If we're already over target AND getting worse, stop
        if current_delta > PRICE_TOLERANCE:
            break

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
            break

        _, chosen = max(candidates)
        allocation[chosen] += 1

        # Track closest solution seen
        new_cost = bouquet_cost(allocation, avg_wholesale_prices)
        new_delta = abs(new_cost - target_price)

        if new_delta < best_delta:
            best_delta = new_delta
            best_allocation = allocation.copy()

    return best_allocation
