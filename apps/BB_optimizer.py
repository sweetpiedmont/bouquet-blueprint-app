import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st

from core.optimization import optimize_bouquets
from core.canonical_recipes import (
    SEASON_KEY_TO_RECIPE_SEASON,
    SEASON_KEY_TO_DISPLAY_LABEL,
    SEASON_KEY_TO_PRICING_LABEL,
)
from core.pricing_data import load_master_pricing
from pathlib import Path


# -----------------------------
# Setup
# -----------------------------

st.title("Bouquet Blueprint Optimizer")
st.caption("Internal testing tool. Not final UI.")

BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "CANONICAL Bouquet Recipe Master Sheet.xlsx"

if "available_stems" not in st.session_state:
    st.session_state.available_stems = {
        "Foundation": 100,
        "Filler": 100,
        "Floater": 100,
        "Finisher": 100,
        "Focal": 100,
        "Foliage": 100,
    }

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

####debug
st.markdown("### Pricing rows used (contains Summer or Fall)")

contains_rows = pricing_df[
    pricing_df["season_raw"].str.contains("Summer|Fall", case=False, na=False)
]

st.write(
    contains_rows
    .groupby("category")["wholesale_price"]
    .mean()
)

### Pretty sure this is debug code
# #st.write(
    #pricing_df.groupby(["category", "season_raw"])
    #.size()
    #.reset_index(name="rows")
#)

# -----------------------------
# Inputs
# -----------------------------

season_key = st.selectbox(
    "Season",
    options=list(SEASON_KEY_TO_DISPLAY_LABEL.keys()),
    format_func=lambda k: SEASON_KEY_TO_DISPLAY_LABEL[k],
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
        step=1,
        key=f"available_{cat}",
        value=st.session_state.available_stems[cat],
    )

st.session_state.available_stems = available_stems

# -----------------------------
# Run optimization
# -----------------------------

if st.button("Optimize bouquets"):

    season_for_pricing = SEASON_KEY_TO_PRICING_LABEL[season_key]

    avg_prices = get_avg_prices_for_season(season_for_pricing)

    ### DEBUG CODE
    st.write("Avg wholesale prices:", avg_prices)

    with st.status("Searching for an optimal bouquet recipe. Please be patient as this can take several minutes.", expanded=True):
        result = optimize_bouquets(
            available_stems=available_stems,
            season_key=season_key,
            target_price=target_price,
            avg_wholesale_prices=avg_prices,
        )

   # Handle hard-stop errors from the optimizer
    if "error" in result:
        st.error(result["error"])
        st.stop()

    # If we get here, a bouquet was found
    st.success("Bouquet recipe generated.")

    st.markdown("### Recommended bouquet")

    st.write(f"**Total stems per bouquet:** {result['total_stems']}")
    st.write(f"**Estimated bouquet cost:** ${result['bouquet_cost']}")
    st.write(f"**Max bouquets possible:** {result['max_bouquets']}")

    # Optional but strongly recommended
    if "price_delta" in result:
        if result.get("within_price_tolerance", False):
            st.caption("Price is within an acceptable range of your target.")
        elif result["price_delta"] < 0:
            st.caption(
                f"This bouquet is ${abs(result['price_delta']):.2f} under your target price. "
                "This can happen with limited availability or early-season flowers."
            )
        else:
            st.caption(
                f"This bouquet is ${result['price_delta']:.2f} over your target price. "
                "This often reflects fuller structure or higher-value stems."
            )

    st.markdown("#### Recipe (stems per bouquet)")
    st.json(result["recipe"])

    st.markdown("#### Stranded stems")
    st.json(result["stranded_stems"])

    st.caption(f"Waste penalty score: {round(result['waste_penalty'], 2)}")
