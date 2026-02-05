import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.compensation import search_best_allocation
from core.recipe_bounds import load_recipe_bounds, convert_bounds_to_percentages


BASE_DIR = Path(__file__).parent.parent
BOUNDS_PATH = BASE_DIR / "data" / "BB_recipe_bounds.xlsx"

available_stems = {
    "Foundation": 100,
    "Focal": 30,
    "Filler": 0,
    "Floater": 20,
    "Finisher": 50,
    "Foliage": 10,
}

raw_bounds = load_recipe_bounds(BOUNDS_PATH)
pct_bounds = convert_bounds_to_percentages(raw_bounds)

stem_bounds = {
    k: {
        "design_min": v["design_min"] * 15,
        "design_max": v["design_max"] * 15,
        "absolute_min": v["absolute_min"] * 15,
        "absolute_max": v["absolute_max"] * 15,
        "stretch_min": (v.get("stretch_min") * 15) if v.get("stretch_min") is not None else None,
    }
    for k, v in pct_bounds["Early Spring"].items()
}

initial = initialize_allocation(
    stem_bounds=stem_bounds,
    available_stems=available_stems,
)

print("Initial allocation:", initial)

result = apply_compensation_with_lookahead(
    allocation=initial,
    available_stems=available_stems,
    stem_bounds=stem_bounds,
    compensation_rules={},  # not used yet
)

print("\nBest allocation:")
for k, v in result["allocation"].items():
    print(f"{k}: {v}")

print("\nEvaluation:")
for k, v in result["evaluation"].items():
    print(f"{k}: {v}")
