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

    recipe_counts = {
        k: round(v * total_stems)
        for k, v in recipe.items()
    }

    st.write(recipe_counts)

    st.info("This is the ideal seasonal recipe before adjusting for availability or pricing.")

    st.subheader("Pricing Summary (Preview)")
    st.write({
        "Estimated wholesale value": "$19.50",
        "GEF applied": "Not yet",
        "Labor included": "Not yet",
        "Final pricing range": "Coming next"
    })