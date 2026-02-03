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
