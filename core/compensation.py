def apply_compensation(
    allocation: dict[str, int],
    available_stems: dict[str, int],
    stem_bounds: dict[str, dict[str, float]],
    compensation_rules: dict[str, set[str]],
) -> dict[str, int]:
    """
    Adjust allocation to maximize bouquet count
    without violating bounds, price, or BB structure.
    """
