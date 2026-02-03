import sys
from pathlib import Path

# Ensure project root is on Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.recipe_bounds import (
    load_recipe_bounds,
    scale_bounds_for_bouquet_size,
)

# -------------------------------------------------
# Setup paths
# -------------------------------------------------

BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "BB Recipe Min-Max.xlsx"

# -------------------------------------------------
# Load bounds
# -------------------------------------------------

bounds = load_recipe_bounds(DATA_PATH)

# -------------------------------------------------
# Test scaling for a known scenario
# -------------------------------------------------

season = "Early Spring"
bouquet_size = 25

available_stems = {
    "Foundation": 100,
    "Focal": 100,
    "Filler": 100,
    "Floater": 100,
    "Finisher": 100,
    "Foliage": 100,
}

scaled_bounds = scale_bounds_for_bouquet_size(
    bounds_for_season=bounds[season],
    bouquet_size=bouquet_size,
    available_stems=available_stems,
)

print("\nScaled bounds for Early Spring, 25 stems:\n")
for category, limits in scaled_bounds.items():
    print(f"{category:12s} → min: {limits['min']}, max: {limits['max']}")
