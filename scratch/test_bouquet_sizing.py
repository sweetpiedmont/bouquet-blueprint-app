import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from core.bouquet_sizing import estimate_bouquet_stem_count
from core.canonical_recipes import CANONICAL_RECIPES


# Sanity-check prices (temporary, for testing only)
avg_prices = {
    "Focal": 2.50,
    "Foundation": 1.75,
    "Filler": 1.25,
    "Floater": 1.50,
    "Finisher": 1.50,
    "Foliage": 0.75,
}

season_key = "early_spring"
target_price = 25.0

stems = estimate_bouquet_stem_count(
    target_price=target_price,
    canonical_percentages=CANONICAL_RECIPES[season_key],
    avg_wholesale_prices=avg_prices,
)

print(f"Estimated stems for ${target_price} ({season_key}): {stems:.2f}")
