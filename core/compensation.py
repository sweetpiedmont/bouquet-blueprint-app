from math import ceil
from typing import Dict

MAX_COMPENSATION_DEPTH = 10

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

def get_effective_lower_bound(
    category: str,
    stem_bounds: dict[str, dict[str, float]],
    available_stems: dict[str, int],
) -> float:
    bounds = stem_bounds[category]

    stretch_min = bounds.get("stretch_min")

    if stretch_min is not None:
        # Category has a stretch min
        if available_stems.get(category, 0) > 0:
            return stretch_min

    # Fallback (or no stretch min)
    return bounds["absolute_min"]

def apply_compensation(
    allocation: dict[str, int],
    available_stems: dict[str, int],
    stem_bounds: dict[str, dict[str, float]],
    compensation_rules: dict[str, set[str]],
) -> dict:
    """
    Phase 3C.2b – single-step compensation attempt
    """

    evaluation = evaluate_allocation(
        allocation=allocation,
        available_stems=available_stems,
    )

    limiting = evaluation["limiting_category"]

    if limiting is None:
        return {
            "allocation": allocation,
            "evaluation": evaluation,
        }

    # Check if limiting category can be reduced
    current = allocation.get(limiting, 0)
    min_allowed = get_effective_lower_bound(
        category=limiting,
        stem_bounds=stem_bounds,
        available_stems=available_stems,
    )

    if current <= min_allowed:
        # Cannot reduce further
        return {
            "allocation": allocation,
            "evaluation": evaluation,
        }

    # Try reducing limiting category by 1 stem
    trial_allocation = allocation.copy()
    trial_allocation[limiting] = current - 1

    trial_eval = evaluate_allocation(
        allocation=trial_allocation,
        available_stems=available_stems,
    )

    # Accept improvement only if bouquet count increases
    if trial_eval["max_bouquets"] > evaluation["max_bouquets"]:
        return {
            "allocation": trial_allocation,
            "evaluation": trial_eval,
        }

    # Otherwise, keep original
    return {
        "allocation": allocation,
        "evaluation": evaluation,
    }

def apply_compensation_until_stable(
    allocation: dict[str, int],
    available_stems: dict[str, int],
    stem_bounds: dict[str, dict[str, float]],
    compensation_rules: dict[str, set[str]],
) -> dict:
    """
    Repeatedly apply single-step compensation until
    no further bouquet-count improvement is possible.
    """

    current_allocation = allocation

    while True:
        result = apply_compensation(
            allocation=current_allocation,
            available_stems=available_stems,
            stem_bounds=stem_bounds,
            compensation_rules=compensation_rules,
        )

        new_allocation = result["allocation"]
        new_eval = result["evaluation"]

        old_eval = evaluate_allocation(
            allocation=current_allocation,
            available_stems=available_stems,
        )

        # Stop if no improvement
        if new_eval["max_bouquets"] <= old_eval["max_bouquets"]:
            return {
                "allocation": current_allocation,
                "evaluation": old_eval,
            }

        # Otherwise accept and keep going
        current_allocation = new_allocation

def apply_single_compensation_step(
    allocation: dict[str, int],
    category: str,
    available_stems: dict[str, int],
    stem_bounds: dict[str, dict[str, float]],
    compensation_rules: dict[str, set[str]],
) -> dict | None:
    """
    Attempt to reduce a specific category by 1 stem,
    respecting effective lower bounds.

    Returns:
        dict with keys {allocation, evaluation} if legal
        None if reduction not allowed
    """

    current = allocation.get(category, 0)

    min_allowed = get_effective_lower_bound(
        category=category,
        stem_bounds=stem_bounds,
        available_stems=available_stems,
    )

    # Cannot reduce further
    if current <= min_allowed:
        return None

    # Try reduction
    trial_allocation = allocation.copy()
    trial_allocation[category] = current - 1

    trial_eval = evaluate_allocation(
        allocation=trial_allocation,
        available_stems=available_stems,
    )

    return {
        "allocation": trial_allocation,
        "evaluation": trial_eval,
    }

def apply_compensation_with_lookahead(
    allocation: dict[str, int],
    available_stems: dict[str, int],
    stem_bounds: dict[str, dict[str, float]],
    compensation_rules: dict[str, set[str]],
) -> dict:
    """
    Phase 3C.3 – bounded lookahead compensation search

    Explore reductions up to MAX_COMPENSATION_DEPTH
    and return the allocation with the highest bouquet count.
    """

    best_allocation = allocation
    best_eval = evaluate_allocation(
        allocation=allocation,
        available_stems=available_stems,
    )

    # frontier holds (allocation, depth)
    frontier = [(allocation, 0)]

    seen = set()

    while frontier:
        current_allocation, depth = frontier.pop(0)

        if depth >= MAX_COMPENSATION_DEPTH:
            continue

        key = tuple(sorted(current_allocation.items()))
        if key in seen:
            continue
        seen.add(key)

        current_eval = evaluate_allocation(
            allocation=current_allocation,
            available_stems=available_stems,
        )

        if current_eval["max_bouquets"] > best_eval["max_bouquets"]:
            best_allocation = current_allocation
            best_eval = current_eval

        # Try reducing each category once
        for category in current_allocation.keys():
            result = apply_single_compensation_step(
                allocation=current_allocation,
                category=category,
                available_stems=available_stems,
                stem_bounds=stem_bounds,
                compensation_rules=compensation_rules,
            )

            if result is None:
                continue

            frontier.append((result["allocation"], depth + 1))

    return {
        "allocation": best_allocation,
        "evaluation": best_eval,
    }

def search_best_allocation(
    initial_allocation: dict[str, int],
    available_stems: dict[str, int],
    stem_bounds: dict[str, dict[str, float]],
    compensation_rules: dict[str, set[str]],
    max_depth: int = 20,
) -> dict:
    """
    Phase 3C.3 – bounded lookahead search for best allocation.

    Explores reductions across all categories, allowing neutral moves,
    and returns the allocation that maximizes bouquet count.
    """

    from collections import deque

    best_allocation = initial_allocation
    best_eval = evaluate_allocation(
        allocation=initial_allocation,
        available_stems=available_stems,
    )

    seen = set()
    queue = deque([(initial_allocation, best_eval, 0)])

    def key(allocation: dict[str, int]) -> tuple:
        return tuple(sorted(allocation.items()))

    seen.add(key(initial_allocation))

    while queue:
        allocation, evaluation, depth = queue.popleft()

        if depth >= max_depth:
            continue

        for category in allocation.keys():
            result = apply_single_compensation_step(
                allocation=allocation,
                category=category,
                available_stems=available_stems,
                stem_bounds=stem_bounds,
                compensation_rules=compensation_rules,
            )

            if result is None:
                continue

            new_alloc = result["allocation"]
            new_eval = result["evaluation"]
            k = key(new_alloc)

            if k in seen:
                continue

            seen.add(k)

            # Update best if strictly better
            if new_eval["max_bouquets"] > best_eval["max_bouquets"]:
                best_allocation = new_alloc
                best_eval = new_eval

            queue.append((new_alloc, new_eval, depth + 1))

    return {
        "allocation": best_allocation,
        "evaluation": best_eval,
    }

