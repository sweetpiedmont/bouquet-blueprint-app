from pathlib import Path
import sys

# Ensure repo root is on path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.optimization import allocate_stems_within_bounds
from core.recipe_bounds import load_recipe_bounds, convert_bounds_to_percentages
from core.bouquet_sizing import apply_percentage_bounds

# -----------------------------
# Load bounds
# -----------------------------

BASE_DIR = ROOT_DIR
BOUNDS_PATH = BASE_DIR / "data" / "BB_recipe_bounds.xlsx"

raw_bounds = load_recipe_bounds(BOUNDS_PATH)
pct_bounds = convert_bounds_to_percentages(raw_bounds)

season = "Early Spring"

# -----------------------------
# Test inputs
# -----------------------------

implied_stems_per_bouquet = 15.0

available_stems = {
    "Foundation": 100,
    "Finisher": 50,
    "Filler": 0,       # intentionally scarce
    "Floater": 20,
    "Focal": 30,
    "Foliage": 10,
}

use_up_priority = [
    "Foundation",
    "Finisher",
    "Filler",
    "Floater",
    "Focal",
    "Foliage",
]

stem_bounds = apply_percentage_bounds(
    total_stems=implied_stems_per_bouquet,
    pct_bounds_for_season=pct_bounds[season],
)

# -----------------------------
# Run allocation
# -----------------------------

allocations = allocate_stems_within_bounds(
    stem_bounds=stem_bounds,
    available_stems=available_stems,
    implied_stems_per_bouquet=implied_stems_per_bouquet,
    use_up_priority=use_up_priority,
)

# -----------------------------
# Inspect results
# -----------------------------

print("Allocations:")
for k, v in allocations.items():
    print(f"{k}: {round(v, 2)}")

print("\nTotal allocated:", round(sum(allocations.values()), 2))
