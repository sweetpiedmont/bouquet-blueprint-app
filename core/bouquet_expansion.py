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
    min_bouquets: int = 1,
) -> bool:
    """
    Check whether adding 1 stem to a category is legal,
    allowing bouquet count to relax if needed.
    """

    current = allocation.get(category, 0)
    bounds = stem_bounds[category]

    # Must not exceed absolute max
    if current + 1 > bounds["absolute_max"]:
        return False

    # Try supporting the stem across fewer bouquets if needed
    for bouquets in range(max_bouquets, min_bouquets - 1, -1):
        required_total = (current + 1) * bouquets
        if available_stems.get(category, 0) >= required_total:
            return True

    return False

def score_addition(
    allocation,
    category,
    stem_bounds,
    available_stems,
    avg_wholesale_prices,
    target_price,
    current_cost,
):
    bounds = stem_bounds[category]

    design_mid = (bounds["design_min"] + bounds["design_max"]) / 2
    distance_penalty = abs((allocation[category] + 1) - design_mid)

    availability = available_stems.get(category, 0)
    stem_price = avg_wholesale_prices[category]

    # NEW: penalize expensive stems as we approach target price
    price_pressure = max(0, current_cost - 0.9 * target_price)
    price_penalty = stem_price * price_pressure

    return availability - distance_penalty * 10 - price_penalty

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

    best_allocation = allocation.copy()
    best_delta = abs(bouquet_cost(allocation, avg_wholesale_prices) - target_price)

    steps = 0

    # ---- expansion loop (price-driven, closest-wins) ----
    while steps < MAX_EXPANSION_STEPS:
        current_cost = bouquet_cost(allocation, avg_wholesale_prices)
        current_delta = abs(current_cost - target_price)

        # If this step is worse than the best we've seen, stop
        if current_delta > best_delta and current_cost > target_price:
            break

        # Otherwise, update best solution if improved
        if current_delta < best_delta:
            best_delta = current_delta
            best_allocation = allocation.copy()

        candidates = []

        for category in allocation:
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
                    avg_wholesale_prices,
                    target_price,
                    current_cost,
                )

                candidates.append((score, category))

        if not candidates:
            break

        _, chosen = max(candidates)
        allocation[chosen] += 1

        steps += 1

    return best_allocation
    

