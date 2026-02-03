import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.recipe_bounds import load_recipe_bounds, convert_bounds_to_percentages

DATA_PATH = ROOT_DIR / "data" / "BB_recipe_bounds.xlsx"

bounds = load_recipe_bounds(DATA_PATH)
pct_bounds = convert_bounds_to_percentages(bounds)

print("Early Spring – percentage bounds:")
for cat, vals in pct_bounds["Early Spring"].items():
    print(cat, vals)
