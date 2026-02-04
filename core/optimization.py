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
