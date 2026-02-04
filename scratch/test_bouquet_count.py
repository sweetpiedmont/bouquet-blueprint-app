from pathlib import Path
import sys

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.optimization import (
    allocate_stems_within_bounds,
    compute_max_bouquets_and_stranded_stems,
)
from core.recipe_bounds import load_recipe_bounds, convert_bounds_to_percentages
from core.bouquet_sizing import apply_percentage_bounds

# -----------------------------
# Load bounds
# -----------------------------

BOUNDS_PATH = ROOT_DIR / "data" / "BB_recipe_bounds.xlsx"
raw_bounds = load_recipe_bounds(BOUNDS_PATH)
pct_bounds = convert_bounds_to_percentages(raw_bounds)

season = "Early Spring"

# -----------------------------
# Inputs
# -----------------------------

implied_stems_per_bouquet = 15.0

available_stems = {
    "Foundation": 100,
    "Finisher": 50,
    "Filler": 0,
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

print("Per-bouquet allocation:")
for k, v in allocations.items():
    print(f"{k}: {round(v, 2)}")

# -----------------------------
# Compute bouquet count
# -----------------------------

result = compute_max_bouquets_and_stranded_stems(
    allocations=allocations,
    available_stems=available_stems,
)

print("\nMax bouquets:", result["max_bouquets"])
print("Limiting category:", result["limiting_category"])

print("\nStranded stems:")
for k, v in result["stranded_stems"].items():
    print(f"{k}: {round(v, 2)}")
