from pathlib import Path
from typing import Dict, Any
import pandas as pd
import math


ANCHOR_BOUQUET_SIZE = 25


def load_recipe_bounds(
    path: Path,
    sheet_name: str | None = None,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Load Bouquet Blueprint recipe bounds from an Excel file.

    Returns a nested dict:

    {
        "early_spring": {
            "Foundation": {
                "design_min_pct": float,
                "design_max_pct": float,
                "absolute_min_pct": float,
                "absolute_max_pct": float,
            },
            ...
        },
        ...
    }

    Notes:
    - All input values are stem counts for a 25-stem bouquet
    - Conversion to percentages happens here
    - No bouquet math or optimizer logic lives in this file
    """

    df = pd.read_excel(path, sheet_name=sheet_name)

    # Normalize column names
    df.columns = df.columns.str.strip()

    required_columns = {
        "Season",
        "Category",
        "Design Min",
        "Design Max",
        "Absolute Min",
        "Absolute Max",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Normalize text fields
    df["Season"] = df["Season"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip()

    bounds: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for _, row in df.iterrows():
        season = row["Season"]
        category = row["Category"]

        bounds.setdefault(season, {})

        bounds[season][category] = {
            "design_min_pct": row["Design Min"] / ANCHOR_BOUQUET_SIZE,
            "design_max_pct": row["Design Max"] / ANCHOR_BOUQUET_SIZE,
            "absolute_min_pct": row["Absolute Min"] / ANCHOR_BOUQUET_SIZE,
            "absolute_max_pct": row["Absolute Max"] / ANCHOR_BOUQUET_SIZE,
        }

    return bounds


def scale_bounds_for_bouquet_size(
    bounds_for_season: Dict[str, Dict[str, float]],
    bouquet_size: int,
    available_stems: Dict[str, int],
) -> Dict[str, Dict[str, int]]:
    """
    Convert percentage-based bounds into integer stem bounds
    for a specific bouquet size and inventory reality.

    Returns:

    {
        "Foundation": {
            "min": int,
            "max": int,
        },
        ...
    }
    """

    scaled: Dict[str, Dict[str, int]] = {}

    for category, b in bounds_for_season.items():
        design_min = math.ceil(b["design_min_pct"] * bouquet_size)
        design_max = math.floor(b["design_max_pct"] * bouquet_size)

        absolute_min = math.ceil(b["absolute_min_pct"] * bouquet_size)
        absolute_max = math.floor(b["absolute_max_pct"] * bouquet_size)

        if available_stems.get(category, 0) == 0:
            effective_min = absolute_min
        else:
            effective_min = design_min

        scaled[category] = {
            "min": effective_min,
            "max": absolute_max,
        }

        if scaled[category]["min"] > scaled[category]["max"]:
            raise ValueError(
                f"Invalid bounds for {category}: "
                f"min {scaled[category]['min']} > max {scaled[category]['max']}"
            )

    return scaled