from pathlib import Path
from typing import Dict
import pandas as pd


REQUIRED_COLUMNS = {
    "Category",
    "Design Min",
    "Design Max",
    "Absolute Min",
    "Absolute Max",
}


IGNORED_SHEETS = {"READ ME"}


def load_recipe_bounds(path: Path) -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Load Bouquet Blueprint recipe bounds from Excel.

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

    # Load all sheets
    sheets = pd.read_excel(path, sheet_name=None)

    bounds: Dict[str, Dict[str, Dict[str, int]]] = {}

    for sheet_name, df in sheets.items():
        if sheet_name in IGNORED_SHEETS:
            continue

        # Normalize column names
        df.columns = df.columns.str.strip()

        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"Sheet '{sheet_name}' is missing required columns: {missing}"
            )

        season_bounds: Dict[str, Dict[str, int]] = {}

        for _, row in df.iterrows():
            category = str(row["Category"]).strip()

            season_bounds[category] = {
                "design_min": int(row["Design Min"]),
                "design_max": int(row["Design Max"]),
                "absolute_min": int(row["Absolute Min"]),
                "absolute_max": int(row["Absolute Max"]),
            }

        bounds[sheet_name] = season_bounds

    return bounds