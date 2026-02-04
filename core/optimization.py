from typing import Dict, List, Optional
from core.canonical_recipes import SEASON_KEY_TO_RECIPE_SEASON
from core.canonical_recipes import CANONICAL_RECIPES
from core.stem_scaling import calculate_stem_recipe
from core.bouquet_sizing import estimate_bouquet_stem_count
from core.recipe_bounds import (
    load_recipe_bounds,
    convert_bounds_to_percentages,
)
from core.bouquet_sizing import apply_percentage_bounds
from pathlib import Path

# -----------------------------
# Configuration (tunable later)
# -----------------------------

MIN_BB_STEMS = 10

MIN_TOTAL_STEMS = 15
MAX_TOTAL_STEMS = 35

# Waste priority weights (higher = worse to strand)
WASTE_WEIGHTS = {
    "Foundation": 5.0,
    "Finisher": 4.0,
    "Floater": 3.0,
    "Filler": 2.0,
    "Focal": 1.0,
    "Foliage": 0.5,
}

### Tier A Allocation

def build_tier_a_allocation(
    implied_stems_per_bouquet: float,
    pct_bounds_for_season: Dict[str, Dict[str, float]],
) -> Optional[Dict[str, int]]:
    """
    Build Tier A (stretch-min) bouquet allocation.

    Returns per-category integer stem counts, or None
    if Tier A is not feasible.
    """

    # Enforce minimum viable BB bouquet size
    if implied_stems_per_bouquet < MIN_BB_STEMS:
        return None

    total_stems = int(implied_stems_per_bouquet)

    allocation: Dict[str, int] = {}
    used_stems = 0

    # Step 1: allocate stretch mins (1 stem each)
    for category, bounds in pct_bounds_for_season.items():
        if bounds.get("stretch_min") is not None:
            allocation[category] = 1
            used_stems += 1

    # Step 2: allocate required category minimums
    for category, bounds in pct_bounds_for_season.items():
        if bounds.get("absolute_min", 0) > 0:
            min_stems = int(round(bounds["absolute_min"] * total_stems))
            allocation[category] = max(allocation.get(category, 0), min_stems)
            used_stems += allocation[category] - allocation.get(category, 0)

    # Check feasibility
    if used_stems > total_stems:
        return None

    # Step 3: distribute remaining stems proportionally
    remaining = total_stems - used_stems

    if remaining > 0:
        flexible_categories = [
            c for c in pct_bounds_for_season
            if allocation.get(c, 0) < int(pct_bounds_for_season[c]["absolute_max"] * total_stems)
        ]

        i = 0
        while remaining > 0 and flexible_categories:
            c = flexible_categories[i % len(flexible_categories)]
            allocation[c] = allocation.get(c, 0) + 1
            remaining -= 1
            i += 1

    return allocation


# -----------------------------
# Core planner
# -----------------------------

def optimize_bouquets(
    available_stems: Dict[str, int],
    season_key: str,
    target_price: float,
    avg_wholesale_prices: Dict[str, float],
    price_tolerance: float = 1.5,
) -> Optional[Dict]:
    """
    Determine the best BB-compliant bouquet configuration
    given available stems and a fixed price target.

    Returns a dict with:
      - total_stems
      - recipe (per-category stem counts)
      - bouquet_cost
      - max_bouquets
      - stranded_stems
      - waste_penalty

    Returns None if no feasible configuration exists.
    """

    recipe_percentages = CANONICAL_RECIPES[season_key]
    
    # ----------------------------------
    # Phase 3A: Bouquet sizing from price
    # ----------------------------------
    implied_stems_per_bouquet = estimate_bouquet_stem_count(
        target_price=target_price,
        canonical_percentages=recipe_percentages,
        avg_wholesale_prices=avg_wholesale_prices,
    )

    # ----------------------------------
    # Phase 3B: Apply recipe bounds
    # ----------------------------------

    BASE_DIR = Path(__file__).parent.parent
    BOUNDS_PATH = BASE_DIR / "data" / "BB_recipe_bounds.xlsx"

    raw_bounds = load_recipe_bounds(BOUNDS_PATH)
    pct_bounds = convert_bounds_to_percentages(raw_bounds)

    stem_bounds = apply_percentage_bounds(
        total_stems=implied_stems_per_bouquet,
        pct_bounds_for_season=pct_bounds[
            SEASON_KEY_TO_RECIPE_SEASON[season_key]
        ],
    )

    return {
        "total_stems": round(implied_stems_per_bouquet, 2),
        "recipe": {},
        "bouquet_cost": target_price,
        "max_bouquets": None,
        "stranded_stems": {},
        "waste_penalty": 0.0,
        "stem_bounds": stem_bounds,
    }

### PHASE 3C

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
