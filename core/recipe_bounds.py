from pathlib import Path
from typing import Dict
import pandas as pd

VALID_CATEGORIES = [
    "Focal",
    "Foundation",
    "Filler",
    "Floater",
    "Finisher",
    "Foliage",
]

SEASON_SHEETS = [
    "Early Spring",
    "Late Spring",
    "Summer-Fall",
]


def load_recipe_bounds(path: Path) -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Load recipe bounds from the canonical Excel file.

    Returns:
    {
        "Early Spring": {
            "Foundation": {
                "design_min": int,
                "design_max": int,
                "absolute_min": int,
                "absolute_max": int,
            },
            ...
        },
        ...
    }
    """

    bounds: Dict[str, Dict[str, Dict[str, int]]] = {}

    for season in SEASON_SHEETS:
        df = pd.read_excel(path, sheet_name=season)

        # Strip column names just in case
        df.columns = df.columns.str.strip()

        season_bounds: Dict[str, Dict[str, int]] = {}

        for category in VALID_CATEGORIES:
            row = df[df["Category"] == category]

            if row.empty:
                raise ValueError(
                    f"Category '{category}' missing from sheet '{season}'"
                )

            row = row.iloc[0]

            season_bounds[category] = {
                "design_min": int(row["Design Min"]),
                "design_max": int(row["Design Max"]),
                "absolute_min": int(row["Absolute Min"]),
                "absolute_max": int(row["Absolute Max"]),
            }

        bounds[season] = season_bounds

    return bounds

def convert_bounds_to_percentages(
    bounds_by_season: dict,
    reference_stems: int = 25,
) -> dict:
    """
    Convert stem-count bounds to percentage bounds.

    Assumes bounds were defined for `reference_stems`.
    """

    pct_bounds = {}

    for season, season_bounds in bounds_by_season.items():
        pct_bounds[season] = {}

        for category, vals in season_bounds.items():
            pct_bounds[season][category] = {
                k: v / reference_stems
                for k, v in vals.items()
            }

    return pct_bounds

