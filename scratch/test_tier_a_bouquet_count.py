import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.optimization import build_tier_a_allocation, compute_max_bouquets
from core.recipe_bounds import load_recipe_bounds, convert_bounds_to_percentages

BASE_DIR = Path(__file__).parent.parent
BOUNDS_PATH = BASE_DIR / "data" / "BB_recipe_bounds.xlsx"

raw_bounds = load_recipe_bounds(BOUNDS_PATH)
pct_bounds = convert_bounds_to_percentages(raw_bounds)

allocation = build_tier_a_allocation(
    implied_stems_per_bouquet=15,
    pct_bounds_for_season=pct_bounds["Early Spring"],
)

available_stems = {
    "Foundation": 100,
    "Focal": 100,
    "Filler": 10,
    "Floater": 10,
    "Finisher": 10,
    "Foliage": 10,
}

print("Tier A allocation:")
print(allocation)

max_bouquets = compute_max_bouquets(
    available_stems=available_stems,
    per_bouquet_allocation=allocation,
)

print("Tier A max bouquets:", max_bouquets)
