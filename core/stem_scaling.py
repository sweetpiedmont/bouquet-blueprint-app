def calculate_stem_recipe(
    total_stems,
    recipe_percentages,
    breakpoint=25,
    foliage_key="Foliage",
    foliage_damping_factor=0.6,
):
    """
    Convert percentage-based recipe into exact stem counts.

    - ≤ breakpoint: normal BB scaling
    - > breakpoint: foliage scales more slowly, all other ratios preserved
    """

    def bb_round(stems, percentages):
        # 1. Raw float counts
        raw = {k: percentages[k] * stems for k in percentages}

        # 2. Floor
        counts = {k: int(raw[k]) for k in raw}

        # 3. Remainder
        remainder = stems - sum(counts.values())

        # 4. BB redistribution order
        redistribution_order = [
            "Foundation",
            "Floater",
            "Filler",
            "Finisher",
            "Focal",
            "Foliage",
        ]

        i = 0
        while remainder > 0:
            cat = redistribution_order[i % len(redistribution_order)]
            counts[cat] += 1
            remainder -= 1
            i += 1

        return counts

    # --- Case 1: at or below breakpoint ---
    if total_stems <= breakpoint:
        return bb_round(total_stems, recipe_percentages)

    # --- Case 2: above breakpoint ---
    base_counts = bb_round(breakpoint, recipe_percentages)
    extra_stems = total_stems - breakpoint

    foliage_share = recipe_percentages.get(foliage_key, 0)
    non_foliage = {
        k: v for k, v in recipe_percentages.items()
        if k != foliage_key
    }

    non_foliage_total = sum(non_foliage.values())
    dampened_foliage_share = foliage_share * foliage_damping_factor
    remaining_share = 1.0 - dampened_foliage_share

    adjusted_extra_percentages = {
        k: (v / non_foliage_total) * remaining_share
        for k, v in non_foliage.items()
    }
    adjusted_extra_percentages[foliage_key] = dampened_foliage_share

    extra_counts = bb_round(extra_stems, adjusted_extra_percentages)

    return {
        k: base_counts.get(k, 0) + extra_counts.get(k, 0)
        for k in recipe_percentages
    }