from math import ceil
from typing import Dict


def initialize_allocation(
    stem_bounds: Dict[str, Dict[str, float]],
    available_stems: Dict[str, int],
) -> Dict[str, int]:
    """
    Phase 3C.1

    Initialize a per-bouquet allocation using:
    stretch_min > design_min > absolute_min

    Rules:
    - Integer stems only
    - stretch_min is used if present and availability > 0
    - design_min is used if stretch_min is None and availability > 0
    - absolute_min is used if availability == 0
    - No compensation
    - No optimization
    """

    allocation: Dict[str, int] = {}

    for category, bounds in stem_bounds.items():
        available = available_stems.get(category, 0)

        stretch_min = bounds.get("stretch_min")
        design_min = bounds["design_min"]
        absolute_min = bounds["absolute_min"]

        if available <= 0:
            # Nothing available → must fall back to absolute min
            allocation[category] = int(ceil(absolute_min))
            continue

        if stretch_min is not None:
            allocation[category] = int(ceil(stretch_min))
        else:
            allocation[category] = int(ceil(design_min))

    return allocation

def evaluate_allocation(
    allocation: dict[str, int],
    available_stems: dict[str, int],
) -> dict:
    """
    Given a per-bouquet allocation, compute:
    - max number of bouquets
    - limiting category
    - stranded stems
    """

    bouquet_limits = {}

    for category, per_bouquet in allocation.items():
        if per_bouquet <= 0:
            continue

        available = available_stems.get(category, 0)
        bouquet_limits[category] = available / per_bouquet

    if not bouquet_limits:
        return {
            "max_bouquets": 0,
            "limiting_category": None,
            "stranded_stems": {},
        }

    limiting_category = min(bouquet_limits, key=bouquet_limits.get)
    max_bouquets = int(bouquet_limits[limiting_category])

    stranded_stems = {
        category: available_stems.get(category, 0)
        - allocation.get(category, 0) * max_bouquets
        for category in allocation
    }

    return {
        "max_bouquets": max_bouquets,
        "limiting_category": limiting_category,
        "stranded_stems": stranded_stems,
    }

def apply_compensation(
    allocation: dict[str, int],
    available_stems: dict[str, int],
    stem_bounds: dict[str, dict[str, float]],
    compensation_rules: dict[str, set[str]],
) -> dict[str, int]:
    """
    Phase 3C.2 (partial)

    Currently:
    - Evaluate baseline allocation
    - Return it unchanged
    """

    evaluation = evaluate_allocation(
        allocation=allocation,
        available_stems=available_stems,
    )

    # TEMP: no compensation yet
    return {
        "allocation": allocation,
        "evaluation": evaluation,
    }

