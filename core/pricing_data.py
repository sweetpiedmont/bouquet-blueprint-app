import pandas as pd

def load_master_pricing(local_path: str) -> pd.DataFrame:
    """
    Load and normalize the Master Variety List pricing data.

    Contract:
    - Sheet name: 'Master Variety List'
    - Required columns:
        - Season
        - Category
        - Avg. WS Price
    """

    # --- Load ---
    df = pd.read_excel(
        local_path,
        sheet_name="Master Variety List"
    )

    # --- Normalize column names ---
    df.columns = df.columns.str.strip()

    # 🔑 DROP unnamed / blank columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]

    # --- Rename to internal-safe names ---
    df = df.rename(columns={
        "Season": "season_raw",
        "Category": "category_raw",
        "Avg. WS Price": "wholesale_price"
    })

    # --- Normalize Season ---
    df["season_raw"] = (
        df["season_raw"]
        .astype(str)
        .str.strip()
    )

    # --- Normalize Category ---
    # Expected format: "1 - Focal", etc.
    df["category"] = (
        df["category_raw"]
        .astype(str)
        .str.split("-", n=1)
        .str[-1]
        .str.strip()
    )

    # --- Normalize Price ---
    df["wholesale_price"] = pd.to_numeric(
        df["wholesale_price"],
        errors="coerce"
    )

    # --- Drop rows that cannot be priced ---
    df = df.dropna(subset=["wholesale_price"])

    df = df.where(pd.notnull(df), None)

    return df