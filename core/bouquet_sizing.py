from typing import Dict


def estimate_bouquet_stem_count(
    target_price: float,
    canonical_percentages: Dict[str, float],
    avg_wholesale_prices: Dict[str, float],
) -> float:
    """
    Estimate bouquet stem count using canonical recipe proportions only.

    - Season-specific via canonical_percentages
    - Uses average wholesale prices per category
    - Returns a continuous stem count (no rounding)
    """

    avg_cost_per_stem = 0.0

    for category, pct in canonical_percentages.items():
        price = avg_wholesale_prices.get(category)

        if price is None:
            raise ValueError(
                f"Missing wholesale price for category '{category}'"
            )

        avg_cost_per_stem += pct * price

    if avg_cost_per_stem <= 0:
        raise ValueError("Average cost per stem must be > 0")

    return target_price / avg_cost_per_stem

from typing import Dict

def apply_percentage_bounds(
    total_stems: float,
    pct_bounds_for_season: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    """
    Convert percentage bounds into continuous stem-count bounds
    for a given total bouquet stem count.

    Returns floats. No rounding, no clamping.
    """

    stem_bounds: Dict[str, Dict[str, float]] = {}

    for category, bounds in pct_bounds_for_season.items():
        stem_bounds[category] = {
            "design_min": bounds["design_min"] * total_stems,
            "design_max": bounds["design_max"] * total_stems,
            "absolute_min": bounds["absolute_min"] * total_stems,
            "absolute_max": bounds["absolute_max"] * total_stems,
        }

    return stem_bounds

