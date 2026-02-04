from pathlib import Path
from core.recipe_bounds import load_recipe_bounds, convert_bounds_to_percentages
from core.optimization import build_tier_a_allocation

BASE_DIR = Path(__file__).parent.parent
BOUNDS_PATH = BASE_DIR / "data" / "BB_recipe_bounds.xlsx"

raw_bounds = load_recipe_bounds(BOUNDS_PATH)
pct_bounds = convert_bounds_to_percentages(raw_bounds)

season = "Early Spring"

allocation = build_tier_a_allocation(
    implied_stems_per_bouquet=15,
    pct_bounds_for_season=pct_bounds[season],
)

print("Tier A allocation:")
print(allocation)

if allocation:
    print("Total stems:", sum(allocation.values()))
