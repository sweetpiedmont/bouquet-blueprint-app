import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.recipe_bounds import load_recipe_bounds, convert_bounds_to_percentages
from core.bouquet_sizing import apply_percentage_bounds

DATA_PATH = ROOT_DIR / "data" / "BB_recipe_bounds.xlsx"

# Load bounds and convert to percentages
bounds = load_recipe_bounds(DATA_PATH)
pct_bounds = convert_bounds_to_percentages(bounds)

# Pretend Phase 3A gave us this stem count
total_stems = 15.02

stem_bounds = apply_percentage_bounds(
    total_stems=total_stems,
    pct_bounds_for_season=pct_bounds["Early Spring"],
)

print(f"Stem bounds for {total_stems:.2f} stems (Early Spring):")
for cat, vals in stem_bounds.items():
    print(cat, {k: round(v, 2) for k, v in vals.items()})
