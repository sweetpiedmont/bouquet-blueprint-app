import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# DEFINITIONS

def invalidate_pricing():
    st.session_state.pop("break_even_price", None)
    st.session_state.pop("recipe_counts", None)

def pricing_zone_from_markup(markup):
    if markup <= 1.05:
        return "🔴 Break-even price (covers costs, no profit)"
    elif markup <= 2.0:
        return "🟢 Farmers market / subscription zone"
    elif markup <= 3.0:
        return "🟠 Made-to-order / Mother’s Day zone"
    else:
        return "🟣 Weddings & events zone"

CANONICAL_RECIPES = {
    "early_spring": {
        "Focal": 0.20,
        "Foundation": 0.45,
        "Filler": 0.05,
        "Floater": 0.10,
        "Finisher": 0.05,
        "Foliage": 0.15,
    },
    "late_spring": {
        "Focal": 0.12,
        "Foundation": 0.43,
        "Filler": 0.10,
        "Floater": 0.10,
        "Finisher": 0.10, 
        "Foliage": 0.15,
    },
    "summer_fall": {
        "Focal": 0.33,
        "Foundation": 0.20,
        "Filler": 0.10,
        "Floater": 0.11,
        "Finisher": 0.11,
        "Foliage": 0.15,
    },
}

SEASON_KEY_TO_RECIPE_SEASON = {
    "early_spring": "Early Spring",
    "late_spring": "Late Spring",
    "summer_fall": "Summer/Fall",
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

pricing_df = load_master_pricing(
    "data/CANONICAL Bouquet Recipe Master Sheet.xlsx"
)

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

# ------------------------------------------------
# Streamlit UI
# ------------------------------------------------

# User inputs
st.subheader("Choose Your Season")

season_choice = st.radio(
    "Are peonies available for you to harvest and use right now?",
    [
        "🌷 No — it’s before peony season (early spring)",
        "🌸 Yes — I have peonies available (late spring)",
        "🌻 No — peony season is over (summer / fall)"
    ],
    on_change=invalidate_pricing,
)

if "early spring" in season_choice:
    season_key = "early_spring"
elif "late spring" in season_choice:
    season_key = "late_spring"
else:
    season_key = "summer_fall"

recipe_season = SEASON_KEY_TO_RECIPE_SEASON[season_key]

st.markdown("---")

st.subheader("Desired Bouquet Size")

total_stems = st.number_input(
    "How many stems are in this bouquet?",
    min_value=10,
    max_value=80,
    value=20,
    step=1,
    on_change=invalidate_pricing,
)

st.markdown("---")

st.subheader("Your Growing Efficiency")

st.caption(
    "This adjusts industry benchmark prices to reflect what it costs *you* to grow flowers."
)

gef = st.slider(
    "",
    min_value=0.50,
    max_value=1.00,
    value=0.65,
    step=0.05,
    on_change=invalidate_pricing,
)

left, middle, right = st.columns([1, 6, 1])

with left:
    st.caption("⬅️ Very efficient")

with middle:
    st.caption("")

with right:
    st.markdown(
        "<div style='text-align: right;'>Higher-cost systems ➡️</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

st.subheader("Labor (Bouquet Assembly Only)")

labor_minutes = st.slider(
    "Time to assemble one bouquet (minutes)",
    min_value=1,
    max_value=15,
    value=3,
    step=1,
    help=(
        "Includes pulling stems, assembling the bouquet, "
        "and securing it (rubber band / sleeve). "
        "Does NOT include harvesting, processing, marketing, or selling."
    ),
    on_change=invalidate_pricing,
)

labor_rate_per_hour = st.number_input(
    "Hourly labor rate ($/hour)",
    min_value=10.0,
    max_value=100.0,
    value=17.0,
    step=1.0
)

labor_cost_per_bouquet = (labor_minutes / 60) * labor_rate_per_hour

st.markdown("---")

st.subheader("Materials (Minimum Supplies)")

materials_cost = st.slider(
    "Materials cost per bouquet ($)",
    min_value=0.02,
    max_value=1.50,
    value=0.30,
    step=0.05,
    help=(
        "Includes only essential supplies like rubber bands "
        "and a basic paper sleeve. "
        "Does NOT include branding or marketing materials."
    ),
    on_change=invalidate_pricing,
)

st.markdown("---")

if st.button("Lock in My Assumptions"):
    recipe = CANONICAL_RECIPES[season_key]
    recipe_season = SEASON_KEY_TO_RECIPE_SEASON[season_key]

    st.subheader("Bouquet Recipe")

    recipe_counts = calculate_stem_recipe(
        total_stems=total_stems,
        recipe_percentages=recipe
)

    st.write(recipe_counts)

    # --- Season mapping for pricing ---
    SEASON_MAP = {
        "Early Spring": ["Early Spring"],
        "Late Spring": ["Late Spring"],
        "Summer/Fall": ["Summer", "Fall"],
    }

    # --- Filter pricing data by recipe season ---
    valid_seasons = SEASON_MAP[recipe_season]

    season_pricing_df = pricing_df[
        pricing_df["season_raw"].str.contains("|".join(valid_seasons), na=False)
    ]

    # --- Compute average price per category ---
    category_avg_prices = (
        season_pricing_df
        .groupby("category")["wholesale_price"]
        .mean()
        .to_dict()
    )

    # --- Compute estimated wholesale value ---
    estimated_wholesale_value = sum(
        recipe_counts.get(category, 0) * category_avg_prices.get(category, 0)
        for category in recipe_counts
    )
    
    estimated_florals_cost = estimated_wholesale_value * gef

    # ---- Break-even price (no profit) ----
    break_even_price_raw = (
        estimated_florals_cost   # flowers (GEF-adjusted)
        + labor_cost_per_bouquet  # labor
        + materials_cost          # rubber band + sleeve
    )

    # Round to nearest $0.10 to remove false precision
    break_even_price = round(break_even_price_raw, 1)

    # 🔑 STORE results
    st.session_state["break_even_price"] = break_even_price
    st.session_state["recipe_counts"] = recipe_counts
    
if "break_even_price" in st.session_state:

    break_even_price = st.session_state["break_even_price"]

    st.markdown("---")

    st.markdown("### 🏷️ Choose Your Selling Price")

    max_price = round(break_even_price * 4.0, 0)

    selling_price = st.slider(
        label="",
        min_value=break_even_price,
        max_value=max_price,
        value=round(break_even_price * 1.5, 1),
        step=0.1,
        key="selling_price_slider"
    )

    components.html(
        f"""
        <div style="display: flex; height: 6px; border-radius: 3px; overflow: hidden;">
            <div style="flex: 0.1; background-color: rgba(204, 0, 0, 0.45);"></div>
            <div style="flex: 0.9; background-color: #e6eb99;"></div>
            <div style="flex: 0.4; background-color: #ffdee7;"></div>
            <div style="flex: 0.6; background-color: #d7f4ff;"></div>
        </div>

            <div style="
                display: flex;
                font-size: 12px;
                margin-top: 4px;
            ">
                <div style="flex: 0.1; text-align: left;">
                    Break-even<br/>
                    <span style="font-size: 11px; opacity: 0.7;">Zone</span>
                </div>

                <div style="flex: 0.9; text-align: center; margin-left: -12px;">
                    Farmers Market<br/>Subscriptions<br/>
                    <span style="font-size: 11px; opacity: 0.7;">Zone</span>
                </div>

                <div style="flex: 0.4; text-align: center;">
                    Mother’s Day<br/>Made-to-Order<br/>
                    <span style="font-size: 11px; opacity: 0.7;">Zone</span>
                </div>

                <div style="flex: 0.6; text-align: center;">
                    Weddings<br/>Events<br/>
                    <span style="font-size: 11px; opacity: 0.7;">Zone</span>
                </div>
            </div>
        """,
        height=70,
    )

    st.markdown(
        f"<h2 style='text-align: center;'>${selling_price:.2f}</h2>",
        unsafe_allow_html=True
    )

    markup = selling_price / break_even_price
    profit_per_bouquet = selling_price - break_even_price

    st.caption(
        f"Markup: {markup:.2f}×  |  "
        f"Profit per bouquet: ${profit_per_bouquet:.2f}"
    )
