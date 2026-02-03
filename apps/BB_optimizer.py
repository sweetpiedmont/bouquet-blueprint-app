import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st

from core.optimization import optimize_bouquets
from core.canonical_recipes import SEASON_KEY_TO_RECIPE_SEASON
from core.pricing_data import load_master_pricing
from pathlib import Path


# -----------------------------
# Setup
# -----------------------------

st.title("Bouquet Blueprint Optimizer (Test Harness)")
st.caption("Internal testing tool. Not final UI.")

BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "CANONICAL Bouquet Recipe Master Sheet.xlsx"


# -----------------------------
# Load pricing data
# -----------------------------

pricing_df = load_master_pricing(DATA_PATH)

# Build average wholesale price per category for selected season
def get_avg_prices_for_season(season_label: str):
    df = pricing_df[pricing_df["season_raw"] == season_label]
    return (
        df.groupby("category")["wholesale_price"]
        .mean()
        .to_dict()
    )


# -----------------------------
# Inputs
# -----------------------------

season_key = st.selectbox(
    "Season",
    options=list(SEASON_KEY_TO_RECIPE_SEASON.keys()),
    format_func=lambda k: SEASON_KEY_TO_RECIPE_SEASON[k],
)

target_price = st.number_input(
    "Target bouquet price",
    min_value=10.0,
    max_value=75.0,
    value=25.0,
    step=1.0,
)

st.subheader("Available stems (this week)")

available_stems = {}
for cat in ["Foundation", "Filler", "Floater", "Finisher", "Focal", "Foliage"]:
    available_stems[cat] = st.number_input(
        cat,
        min_value=0,
        value=100,
        step=10,
    )


# -----------------------------
# Run optimization
# -----------------------------

if st.button("Optimize bouquets"):

    avg_prices = get_avg_prices_for_season(
        SEASON_KEY_TO_RECIPE_SEASON[season_key]
    )

    result = optimize_bouquets(
        available_stems=available_stems,
        season_key=season_key,
        target_price=target_price,
        avg_wholesale_prices=avg_prices,
    )

    if result is None:
        st.error("No feasible bouquet configuration found at this price.")
    else:
        st.success("Feasible bouquet configuration found.")

        st.markdown("### Recommended bouquet")

        st.write(f"**Total stems per bouquet:** {result['total_stems']}")
        st.write(f"**Estimated bouquet cost:** ${result['bouquet_cost']}")
        st.write(f"**Max bouquets possible:** {result['max_bouquets']}")

        st.markdown("#### Recipe (stems per bouquet)")
        st.json(result["recipe"])

        st.markdown("#### Stranded stems")
        st.json(result["stranded_stems"])

        st.caption(f"Waste penalty score: {round(result['waste_penalty'], 2)}")

#prove bounds scaling works
from pathlib import Path
from core.recipe_bounds import load_recipe_bounds, scale_bounds_for_bouquet_size

DATA_PATH = Path("data/BB Recipe Min-Max.xlsx")

bounds = load_recipe_bounds(DATA_PATH)

season = "Early Spring"
bouquet_size = 25

available_stems = {
    "Foundation": 100,
    "Focal": 100,
    "Filler": 100,
    "Floater": 100,
    "Finisher": 100,
    "Foliage": 100,
}

scaled = scale_bounds_for_bouquet_size(
    bounds_for_season=bounds[season],
    bouquet_size=bouquet_size,
    available_stems=available_stems,
)

st.write("Scaled bounds:", scaled)
