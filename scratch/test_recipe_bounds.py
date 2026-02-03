import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.recipe_bounds import load_recipe_bounds

DATA_PATH = ROOT_DIR / "data" / "BB_recipe_bounds.xlsx"

bounds = load_recipe_bounds(DATA_PATH)

print("\nLoaded seasons:")
for season in bounds:
    print(season)

print("\nEarly Spring bounds:")
for cat, vals in bounds["Early Spring"].items():
    print(cat, vals)
