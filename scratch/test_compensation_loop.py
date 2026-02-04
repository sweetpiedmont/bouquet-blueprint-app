import sys
from pathlib import Path

# ---- path setup so `core` imports work ----
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.compensation import (
    apply_compensation_until_stable,
)
from core.recipe_bounds import (
    load_recipe_bounds,
    convert_bounds_to_percentages,
)
from core.bouquet_sizing import apply_percentage_bounds

# -----------------------------
# Test setup (matches prior tests)
# -----------------------------

DATA_PATH = ROOT_DIR / "data" / "BB_recipe_bounds.xlsx"
season = "Early Spring"

available_stems = {
    "Focal": 30,
    "Foundation": 100,
    "Filler": 0,
    "Floater": 20,
    "Finisher": 50,
    "Foliage": 10,
}

# Implied bouquet size from earlier test
implied_stems_per_bouquet = 15.0

# Compensation rules (your latest version)
COMPENSATION_RULES = {
    "Filler": {"Foundation", "Finisher", "Floater"},
    "Floater": {"Foundation", "Finisher", "Filler"},
    "Finisher": {"Foundation", "Filler", "Floater"},
    "Foliage": {"Foundation", "Finisher", "Filler", "Floater"},
    "Focal": {"Foundation"},
    "Foundation": set(),
}

# -----------------------------
# Load and scale bounds
# -----------------------------

raw_bounds = load_recipe_bounds(DATA_PATH)
pct_bounds = convert_bounds_to_percentages(raw_bounds)

stem_bounds = apply_percentage_bounds(
    total_stems=implied_stems_per_bouquet,
    pct_bounds_for_season=pct_bounds[season],
)

# -----------------------------
# Initial allocation (what you already tested)
# -----------------------------

initial_allocation = {
    "Focal": 3,
    "Foundation": 3,
    "Filler": 0,
    "Floater": 2,
    "Finisher": 1,
    "Foliage": 2,
}

# -----------------------------
# Run looped compensation
# -----------------------------

result = apply_compensation_until_stable(
    allocation=initial_allocation,
    available_stems=available_stems,
    stem_bounds=stem_bounds,
    compensation_rules=COMPENSATION_RULES,
)

# -----------------------------
# Output
# -----------------------------

print("\nFinal allocation:")
for k, v in result["allocation"].items():
    print(f"{k}: {v}")

print("\nFinal evaluation:")
for k, v in result["evaluation"].items():
    print(f"{k}: {v}")
