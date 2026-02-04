import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.recipe_bounds import load_recipe_bounds, convert_bounds_to_percentages
from core.bouquet_sizing import apply_percentage_bounds
from core.compensation import initialize_allocation

# -----------------------------
# Setup
# -----------------------------

BASE_DIR = Path(__file__).parent.parent
BOUNDS_PATH = BASE_DIR / "data" / "BB_recipe_bounds.xlsx"

season = "Early Spring"
implied_stems_per_bouquet = 15.0

available_stems = {
    "Focal": 30,
    "Foundation": 100,
    "Filler": 0,       # intentionally scarce
    "Floater": 20,
    "Finisher": 50,
    "Foliage": 10,
}

# -----------------------------
# Load bounds
# -----------------------------

raw_bounds = load_recipe_bounds(BOUNDS_PATH)
pct_bounds = convert_bounds_to_percentages(raw_bounds)

stem_bounds = apply_percentage_bounds(
    total_stems=implied_stems_per_bouquet,
    pct_bounds_for_season=pct_bounds[season],
)

# -----------------------------
# Run initializer
# -----------------------------

allocation = initialize_allocation(
    stem_bounds=stem_bounds,
    available_stems=available_stems,
)

print("Initializer allocation:")
for k, v in allocation.items():
    print(f"{k}: {v}")

print("Total stems:", sum(allocation.values()))
