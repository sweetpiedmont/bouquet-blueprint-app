import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path

from core.canonical_recipes import (
    CANONICAL_RECIPES,
    SEASON_KEY_TO_RECIPE_SEASON,
)

from core.pricing_data import load_master_pricing

from core.stem_scaling import calculate_stem_recipe

def invalidate_pricing():
    st.session_state.pop("break_even_price", None)
    st.session_state.pop("recipe_counts", None)

def normalize_pricing_season(recipe_season: str) -> str:
    """
    Normalize season labels coming from canonical_recipes
    to match pricing / Excel conventions.
    """
    return recipe_season.replace("-", "/")

# ------------------------------------------------
# Load pricing data
# ------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "CANONICAL Bouquet Recipe Master Sheet.xlsx"

pricing_df = load_master_pricing(DATA_PATH)

# --- Password gate ---
APP_PASSWORD = st.secrets.get("BB_APP_PASSWORD")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(
    "<h1>Bouquet Blueprint<sup style='font-size: 0.5em;'>™</sup> Pricing Tool</h1>"
    "<p style='margin-top: -10px; opacity: 0.7;'>Beta test version</p>",
    unsafe_allow_html=True
)

    password = st.text_input(
        "Enter beta access password",
        type="password"
    )

    if password:
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")

    st.stop()

# ------------------------------------------------
# Streamlit UI
# ------------------------------------------------
st.markdown(
    "<h1>Bouquet Blueprint<sup style='font-size: 0.5em;'>™</sup> Pricing Tool "
    "<span style='font-size: 0.6em; font-weight: 400;'>(Beta Test Version)</span></h1>",
    unsafe_allow_html=True
)

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
pricing_season = normalize_pricing_season(recipe_season)

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

st.markdown(
    "<p style='font-size: 0.9em; opacity: 0.85;'>"
    "<strong>Growing efficiency</strong> reflects how costly it is for your farm "
    "to produce usable flower stems."
    "</p>"
    "<p style='font-size: 0.9em; opacity: 0.85;'>"
    "Lower values mean tighter systems, better sell-through, and fewer wasted stems. "
    "Higher values mean more waste, higher labor or input costs, and less efficient systems."
    "</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<ul style='font-size: 0.85em; opacity: 0.75; margin-top: 0.25em;'>"
    "<li><strong>0.5–0.7:</strong> Highly efficient growing systems</li>"
    "<li><strong>0.7–0.9:</strong> Moderately efficient systems</li>"
    "<li><strong>0.9–1.0:</strong> High-cost growing systems</li>"
    "<li><strong>Above 1.0:</strong> Growing costs exceed wholesale prices</li>"
    "</ul>",
    unsafe_allow_html=True
)

gef = st.slider(
    "How efficient is your operation?",
    min_value=0.50,
    max_value=1.50,
    value=0.65,
    step=0.05,
    on_change=invalidate_pricing,
)

min_gef = 0.4
max_gef = 1.5
breakpoint_gef = 1.0

left_pct = (breakpoint_gef - min_gef) / (max_gef - min_gef) * 100
right_pct = 100 - left_pct

components.html(
    f"""
    <div style="margin-top: 6px; font-family: sans-serif;">
        <!-- BAR -->
        <div style="display: flex; height: 6px; border-radius: 3px; overflow: hidden;">
            <div style="width: {left_pct}%; background-color: #e6eb99;"></div>
            <div style="width: {right_pct}%; background-color: #ff4582;"></div>
        </div>

        <!-- LABELS -->
        <div style="
            display: flex;
            font-size: 12px;
            margin-top: 6px;
            position: relative;
        ">
            <div style="width: {left_pct}%; text-align: left;">
                Highly efficient<br/>
                growing operation
            </div>

            <div style="
                position: absolute;
                left: {left_pct}%;
                transform: translateX(-50%);
                width: 240px;
                text-align: center;
                white-space: normal;
                font-weight: 500;
            ">
                ⚠️ 1.0
            </div>

            <div style="width: {right_pct}%; text-align: right;">
                Highly <u><strong>in</strong></u>efficient<br/>
                growing operation
            </div>
        </div>
    </div>
    """,
    height=70,
)

st.caption(
    "⚠️ Above a growing efficiency of 1.0, it costs you more to grow your flowers "
    "than it would (on average) to purchase them wholesale. "
    "Reducing growing costs is critical to long-term profitability."
)

st.markdown("---")

st.subheader("Labor (Bouquet Assembly Only)")

labor_minutes = st.slider(
    "How much time does it take to assemble one bouquet (in minutes)",
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

st.subheader("Bouquet Packaging")

materials_cost = st.slider(
    "What materials will be sold with the bouquet (in $)",
    min_value=0.02,
    max_value=2.00,
    value=0.30,
    format="$%.2f",
    step=0.05,
    help=(
        "Include essentials like rubber bands "
        "and a basic paper sleeve (around $0.30 total). "
        "Also consider 'extras' like stickers, "
        "tags, ink-stamped logos, hydration packs, or "
        "anything else that is sold with the bouquet. "
        "Do NOT include buckets, snips, or other production "
        "equipment that stays on the farm."
    ),
    on_change=invalidate_pricing,
)

st.markdown("---")

if st.button("Lock in My Assumptions"):
    recipe = CANONICAL_RECIPES[season_key]
    recipe_season = SEASON_KEY_TO_RECIPE_SEASON[season_key]

    st.markdown(
        "<h3>Bouquet Blueprint<sup style='font-size: 0.6em;'>™</sup> Recipe</h3>",
        unsafe_allow_html=True
    )

    recipe_counts = calculate_stem_recipe(
        total_stems=total_stems,
        recipe_percentages=recipe
)

    recipe_df = (
        pd.DataFrame.from_dict(recipe_counts, orient="index", columns=["Stems"])
        .reset_index()
        .rename(columns={"index": "Flower Type"})
    )

    left, _ = st.columns([2, 6])

    with left:
        st.table(recipe_df)

    st.markdown(
        "<p style='font-size: 0.85em; opacity: 0.75; margin-top: 0.75em;'>"
        "Substitutions within supporting ingredients "
        "(fillers, floaters, finishers, foliage) usually have minimal impact on price."
        "<br><br>"
        "<strong>Focal flowers are different.</strong> Swapping them with other flower types can significantly "
        "change the value of the bouquet."
        "</p>",
        unsafe_allow_html=True
    )

    # --- Season mapping for pricing ---
    SEASON_MAP = {
        "Early Spring": ["Early Spring"],
        "Late Spring": ["Late Spring"],
        "Summer/Fall": ["Summer/Fall"],
    }

    # --- Filter pricing data by recipe season ---
    valid_seasons = SEASON_MAP[pricing_season]

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
        "Move the slider to see how price affects potential profit",
        min_value=break_even_price,
        max_value=max_price,
        value=round(break_even_price * 1.5, 1),
        step=0.1,
        format="$%.2f",
        key="selling_price_slider"
    )

    components.html(
        f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                    Roboto, Helvetica, Arial, sans-serif;">

            <div style="display: flex; height: 6px; border-radius: 3px; overflow: hidden;">
                <div style="flex: 0.1; background-color: rgba(204, 0, 0, 0.45);"></div>
                <div style="flex: 0.6; background-color: #e6eb99;"></div>
                <div style="flex: 0.7; background-color: #ffdee7;"></div>
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

                <div style="flex: 0.6; text-align: center; margin-left: -12px;">
                    Farmers Market,<br/>Subscriptions<br/>
                    <span style="font-size: 11px; opacity: 0.7;">Zone</span>
                </div>

                <div style="flex: 0.7; text-align: center;">
                    Mother’s Day,<br/>Made-to-Order<br/>
                    <span style="font-size: 11px; opacity: 0.7;">Zone</span>
                </div>

                <div style="flex: 0.6; text-align: center;">
                    Weddings,<br/>Events<br/>
                    <span style="font-size: 11px; opacity: 0.7;">Zone</span>
                </div>
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
        f"Potential profit per bouquet: ${profit_per_bouquet:.2f}"
    )

    st.markdown(
        "<p style='font-size: 0.85em; opacity: 0.75; text-align: left;'>"
        "<em>Pricing zones are approximate guides, not rules, and do not include costs associated with selling, such as bringing bouquets to the farmers market or making deliveries.</em>"
        "</p>"
        "<p style='font-size: 0.85em; opacity: 0.75; text-align: left;'>"
        "Your final price should reflect these costs, as well as what your market will bear "
        "and the profit you need this bouquet to earn."
        "</p>"
        "<p style='font-size: 0.85em; opacity: 0.75; text-align: left;'>"
        "Use the zones as context — then choose the price that fits your business."
        "</p>",
        unsafe_allow_html=True
    )
