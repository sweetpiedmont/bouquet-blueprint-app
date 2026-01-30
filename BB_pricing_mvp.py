import streamlit as st
import pandas as pd

# ------------------------------------------------
# Streamlit UI
# ------------------------------------------------

# User inputs
selected_month = st.selectbox("Select Month", [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

wholesale_price = st.number_input("Target Price per Bouquet ($)", min_value=0.0, step=0.5)
num_bouquets = st.number_input("Number of Bouquets", min_value=1, step=1)

num_focal = st.number_input("Available Focal Flowers", min_value=0, step=1)
num_foundation = st.number_input("Available Foundation Flowers", min_value=0, step=1)
num_filler = st.number_input("Available Filler Flowers", min_value=0, step=1)
num_floater = st.number_input("Available Floater Flowers", min_value=0, step=1)
num_finisher = st.number_input("Available Finisher Flowers", min_value=0, step=1)
num_foliage = st.number_input("Available Foliage Stems", min_value=0, step=1)

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