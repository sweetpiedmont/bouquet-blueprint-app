import streamlit as st
import pandas as pd

CANONICAL_RECIPES = {
    "early_spring": {
        "Focal": 0.25,
        "Foundation": 0.45,
        "Filler": 0.05,
        "Floater": 0.05,
        "Finisher": 0.05,
        "Foliage": 0.15,
    },
    "late_spring": {
        "Focal": 0.10,
        "Foundation": 0.45,
        "Filler": 0.10,
        "Floater": 0.10,
        "Finisher": 0.10,
        "Foliage": 0.15,
    },
    "summer_fall": {
        "Focal": 0.15,
        "Foundation": 0.40,
        "Filler": 0.08,
        "Floater": 0.11,
        "Finisher": 0.11,
        "Foliage": 0.15,
    },
}

@st.cache_data
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

    return df

pricing_df = load_master_pricing(
    "/Users/sharon/Library/CloudStorage/OneDrive-Personal/Bouquet Recipes/CANONICAL Bouquet Recipe Master Sheet.xlsx"
)

st.write(pricing_df.head())

def calculate_stem_recipe(total_stems, recipe_percentages):
    """
    Convert percentage-based recipe into exact stem counts
    while guaranteeing total stems and BB-style redistribution.
    """

    # 1. Raw float counts
    raw_counts = {
        k: recipe_percentages[k] * total_stems
        for k in recipe_percentages
    }

    # 2. Floor everything
    stem_counts = {
        k: int(raw_counts[k])
        for k in raw_counts
    }

    # 3. Calculate remainder
    used_stems = sum(stem_counts.values())
    remainder = total_stems - used_stems

    # 4. BB-style redistribution order
    redistribution_order = [
        "Foundation",
        "Focal",
        "Foliage",
        "Filler",
        "Floater",
        "Finisher",
    ]

    i = 0
    while remainder > 0:
        category = redistribution_order[i % len(redistribution_order)]
        stem_counts[category] += 1
        remainder -= 1
        i += 1

    return stem_counts

# ------------------------------------------------
# Streamlit UI
# ------------------------------------------------

# User inputs
season_choice = st.radio(
    "Are peonies available for you to harvest and use right now?",
    [
        "🌷 No — it’s before peony season (early spring)",
        "🌸 Yes — I have peonies available (late spring)",
        "🌻 No — peony season is over (summer / fall)"
    ]
)

if "early spring" in season_choice:
    season_key = "early_spring"
elif "late spring" in season_choice:
    season_key = "late_spring"
else:
    season_key = "summer_fall"

st.markdown("---")

total_stems = st.number_input(
    "How many stems are in this bouquet?",
    min_value=10,
    max_value=80,
    value=20,
    step=1
)

if st.button("Run Pricing MVP"):
    recipe = CANONICAL_RECIPES[season_key]

    st.subheader("Ideal Bouquet Recipe (by stem count)")

    recipe_counts = calculate_stem_recipe(
        total_stems=total_stems,
        recipe_percentages=recipe
)

    st.write(recipe_counts)

    st.info("This is the ideal seasonal recipe before adjusting for availability or pricing.")

    st.subheader("Pricing Summary (Preview)")
    st.write({
        "Estimated wholesale value": "$19.50",
        "GEF applied": "Not yet",
        "Labor included": "Not yet",
        "Final pricing range": "Coming next"
    })