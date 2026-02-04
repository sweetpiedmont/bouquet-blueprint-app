### PHASE 3C - Allocation, scarcity and compensation

def allocate_stems_within_bounds(
    stem_bounds: Dict[str, Dict[str, float]],
    available_stems: Dict[str, int],
    implied_stems_per_bouquet: float,
    use_up_priority: List[str],
) -> Dict[str, float]:
    """
    Allocate stems across categories starting from design_min
    and incrementally distributing remaining stems within bounds.

    Returns:
        Dict[str, float]: per-category stem allocation (floats)
    """
    pass

    # 1. Initialize allocations at design_min
    allocations: Dict[str, float] = {}

    for category, bounds in stem_bounds.items():
        if available_stems.get(category, 0) <= 0:
            allocations[category] = bounds["absolute_min"]
        else:
            allocations[category] = bounds["design_min"]

    # Total stems allocated so far
    allocated_total = sum(allocations.values())

    # Remaining stems to allocate
    remaining_stems = implied_stems_per_bouquet - allocated_total

    if remaining_stems < 0:
        # Cannot even meet design minimums
        return allocations
    
    # 2. Compute availability pressure ratios
    availability_pressure: Dict[str, float] = {}

    for category in allocations:
        canonical_pct = stem_bounds[category]["design_min"] / max(
            implied_stems_per_bouquet, 1e-6
        )

        expected_needed = canonical_pct * implied_stems_per_bouquet

        available = available_stems.get(category, 0)

        if expected_needed <= 0:
            availability_pressure[category] = 0.0
        else:
            availability_pressure[category] = available / expected_needed

    # 3. Incremental allocation rounds
    INCREMENT = implied_stems_per_bouquet * 0.02

    while remaining_stems > 1e-6:
        # Eligible categories for this round
        eligible = []

        for category in use_up_priority:
            bounds = stem_bounds[category]
            current = allocations.get(category, 0.0)

            if current + INCREMENT > bounds["absolute_max"]:
                continue

            if available_stems.get(category, 0) <= 0 and bounds["absolute_min"] > 0:
                continue

            eligible.append(category)

        if not eligible:
            break

        # Compute weighted scores
        scores = {}
        for category in eligible:
            priority_weight = (
                len(use_up_priority) - use_up_priority.index(category)
            )
            pressure = availability_pressure.get(category, 1.0)

            scores[category] = priority_weight * pressure

        # Choose best category this round
        chosen = max(scores, key=scores.get)

        # Allocate increment (clamped)
        allocation = min(
            INCREMENT,
            remaining_stems,
            stem_bounds[chosen]["absolute_max"] - allocations[chosen],
        )

        allocations[chosen] += allocation
        remaining_stems -= allocation

    return allocations

def compute_max_bouquets_and_stranded_stems(
    allocations: Dict[str, float],
    available_stems: Dict[str, int],
) -> Dict:
    """
    Given per-bouquet allocations and total available stems,
    compute the maximum number of bouquets and stranded stems.

    Returns:
        {
            "max_bouquets": int,
            "limiting_category": str,
            "stranded_stems": Dict[str, float],
        }
    """
    bouquet_limits = {}

    for category, per_bouquet in allocations.items():
        if per_bouquet <= 0:
            continue

        available = available_stems.get(category, 0)
        bouquet_limits[category] = available / per_bouquet

    if not bouquet_limits:
        return {
            "max_bouquets": 0,
            "limiting_category": None,
            "stranded_stems": {},
        }

    limiting_category = min(bouquet_limits, key=bouquet_limits.get)
    max_bouquets = int(bouquet_limits[limiting_category])

    stranded_stems = {
        category: available_stems.get(category, 0)
        - allocations.get(category, 0) * max_bouquets
        for category in allocations
    }

    return {
        "max_bouquets": max_bouquets,
        "limiting_category": limiting_category,
        "stranded_stems": stranded_stems,
    }
