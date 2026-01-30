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

st.markdown("---")

if st.button("Run Pricing MVP"):
    st.subheader("Bouquet Recipe (Preview)")
    st.write({
        "Focal Flowers": 2,
        "Foundation Flowers": 5,
        "Filler Flowers": 1,
        "Floater Flowers": 1,
        "Finisher Flowers": 0,
        "Foliage Stems": 3,
    })

    st.subheader("Pricing Summary (Preview)")
    st.write({
        "Estimated wholesale value": "$19.50",
        "GEF applied": "Not yet",
        "Labor included": "Not yet",
        "Final pricing range": "Coming next"
    })