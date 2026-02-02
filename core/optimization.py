from typing import Dict, List, Optional

from core.canonical_recipes import CANONICAL_RECIPES
from core.stem_scaling import calculate_stem_recipe


# -----------------------------
# Configuration (tunable later)
# -----------------------------

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
    solutions: List[Dict] = []

    for total_stems in range(MIN_TOTAL_STEMS, MAX_TOTAL_STEMS + 1):

        # 1. Build BB-compliant recipe
        recipe = calculate_stem_recipe(
            total_stems=total_stems,
            recipe_percentages=recipe_percentages,
        )

        # 2. Compute bouquet cost
        bouquet_cost = 0.0
        for cat, count in recipe.items():
            price = avg_wholesale_prices.get(cat)
            if price is None:
                bouquet_cost = None
                break
            bouquet_cost += count * price

        if bouquet_cost is None:
            continue

        # 3. Enforce price guardrail
        if abs(bouquet_cost - target_price) > price_tolerance:
            continue

        # 4. Determine max bouquets possible
        try:
            max_bouquets = min(
                available_stems[cat] // recipe[cat]
                for cat in recipe
                if recipe[cat] > 0
            )
        except KeyError:
            # missing category in available_stems
            continue

        if max_bouquets <= 0:
            continue

        # 5. Compute stranded stems
        stranded = {
            cat: available_stems[cat] - recipe[cat] * max_bouquets
            for cat in recipe
        }

        # 6. Compute weighted waste penalty
        waste_penalty = sum(
            stranded.get(cat, 0) * WASTE_WEIGHTS.get(cat, 1.0)
            for cat in stranded
        )

        solutions.append({
            "total_stems": total_stems,
            "recipe": recipe,
            "bouquet_cost": round(bouquet_cost, 2),
            "max_bouquets": max_bouquets,
            "stranded_stems": stranded,
            "waste_penalty": waste_penalty,
        })

    if not solutions:
        return None

    # 7. Select best solution
    best = min(
        solutions,
        key=lambda s: (
            s["waste_penalty"],                 # primary
            -s["max_bouquets"],                 # secondary
            abs(s["bouquet_cost"] - target_price),  # tertiary
        )
    )

    return best