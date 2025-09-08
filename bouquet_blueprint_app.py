import streamlit as st
import pandas as pd   # <-- THIS needs to be here
import pulp
from datetime import datetime

def run_optimization(selected_month, retail_price, num_bouquets,
                     num_focal, num_foundation, num_filler,
                     num_floater, num_finisher, num_foliage):

    # Load Excel Master Variety List
    data = pd.read_excel(
        "data/Copy of Bouquet Recipe Master Sheet v5 09.07.2025.xlsx",
        sheet_name="Master Variety List"
    )

    # Clean up price column: force numeric, replace errors/NaN with 0
    data["Avg. WS Price"] = pd.to_numeric(
        data["Avg. WS Price"], errors="coerce"
    ).fillna(0)

    # Standardize column names for optimizer
    data = data.rename(columns={
        "Category": "FlowerType",
        "Avg. WS Price": "RetailCostPerStem"
    })

    # Clean up FlowerType (remove "2 - " etc.)
    data["FlowerType"] = (
        data["FlowerType"]
        .astype(str)
        .str.split("-")
        .str[-1]
        .str.strip()
    )

    # Ensure price is numeric
    data["RetailCostPerStem"] = pd.to_numeric(
        data["RetailCostPerStem"], errors="coerce"
    )

    # Strip whitespace from Season
    data["Season"] = data["Season"].astype(str).str.strip()

    # Map month to season
    month_to_season = {
        "January": "Winter", "February": "Winter", "March": "Early Spring",
        "April": "Early Spring", "May": "Late Spring", "June": "Late Spring",
        "July": "Summer", "August": "Summer", "September": "Fall",
        "October": "Fall", "November": "Winter", "December": "Winter"
    }
    selected_season = month_to_season.get(selected_month, "Unknown Season")

    # Price range around user price
    price_range_lower = retail_price - 0.5
    price_range_upper = retail_price + 1.0

    # Flower categories
    selected_flower_type = ["Focal", "Foundation", "Filler", "Floater", "Finisher", "Foliage"]

    # Filter by season and type
    filtered_data = data[
        (data["Season"] == selected_season) &
        (data["FlowerType"].isin(selected_flower_type))
    ]

    # -----------------------
    # Debug: show filtered data in Streamlit
    # -----------------------
    st.write(f"### Debug: Filtered data for {selected_month} ({selected_season})")
    st.dataframe(filtered_data[["Flower", "FlowerType", "Season", "RetailCostPerStem"]])

    # Average cost per flower type
    average_retail_costs = (
        filtered_data.groupby("FlowerType")["RetailCostPerStem"]
        .mean()
        .to_dict()
    )

    avg_costs = {
        "Focal": average_retail_costs.get("Focal", 0.0),
        "Foundation": average_retail_costs.get("Foundation", 0.0),
        "Filler": average_retail_costs.get("Filler", 0.0),
        "Floater": average_retail_costs.get("Floater", 0.0),
        "Finisher": average_retail_costs.get("Finisher", 0.0),
        "Foliage": average_retail_costs.get("Foliage", 0.0),
    }

    retail_price = float(retail_price)

   # Base upper bounds (assumes $35 bouquet baseline)
    if selected_season == "Late Spring":
        base_upper_bound_focal = 1
    else:
        base_upper_bound_focal = 3
        base_upper_bound_foundation = 20
        base_upper_bound_filler = 2
        base_upper_bound_floater = 3
        base_upper_bound_finisher = 2
        base_upper_bound_foliage = 2

    # Scale bounds by bouquet price
    adjusted_bounds = {
        "Focal": round(base_upper_bound_focal * (retail_price / 35)),
        "Foundation": round(base_upper_bound_foundation * (retail_price / 35)),
        "Filler": round(base_upper_bound_filler * (retail_price / 35)),
        "Floater": round(base_upper_bound_floater * (retail_price / 35)),
        "Finisher": round(base_upper_bound_finisher * (retail_price / 35)),
        "Foliage": round(base_upper_bound_foliage * (retail_price / 35)),
    }

    # PuLP model
    model = pulp.LpProblem("Bouquet_Optimization", pulp.LpMinimize)

    use_focal = pulp.LpVariable("use_focal", 1, adjusted_bounds["Focal"], cat="Integer")
    use_foundation = pulp.LpVariable("use_foundation", 3, adjusted_bounds["Foundation"], cat="Integer")
    use_filler = pulp.LpVariable("use_filler", 1, adjusted_bounds["Filler"], cat="Integer")
    use_floater = pulp.LpVariable("use_floater", 2, adjusted_bounds["Floater"], cat="Integer")
    use_finisher = pulp.LpVariable("use_finisher", 1, adjusted_bounds["Finisher"], cat="Integer")
    use_foliage = pulp.LpVariable("use_foliage", 2, adjusted_bounds["Foliage"], cat="Integer")

    total_cost = (
        use_focal * avg_costs["Focal"] +
        use_foundation * avg_costs["Foundation"] +
        use_filler * avg_costs["Filler"] +
        use_floater * avg_costs["Floater"] +
        use_finisher * avg_costs["Finisher"] +
        use_foliage * avg_costs["Foliage"]
    )

    num_bouquets = int(num_bouquets)

    # Constraints
    model += use_focal * num_bouquets <= num_focal
    model += use_foundation * num_bouquets <= num_foundation
    model += use_filler * num_bouquets <= num_filler
    model += use_floater * num_bouquets <= num_floater
    model += use_finisher * num_bouquets <= num_finisher
    model += use_foliage * num_bouquets <= num_foliage
    model += (total_cost >= price_range_lower)
    model += (total_cost <= price_range_upper)

    # Objective: minimize cost
    model += total_cost
    from pulp import COIN_CMD
    model.solve(COIN_CMD(path="/usr/local/bin/cbc", msg=1))

    # Results
    optimized_results = {
        "optimized_use_focal": use_focal.varValue,
        "optimized_use_foundation": use_foundation.varValue,
        "optimized_use_filler": use_filler.varValue,
        "optimized_use_floater": use_floater.varValue,
        "optimized_use_finisher": use_finisher.varValue,
        "optimized_use_foliage": use_foliage.varValue,
        "leftover_focal": num_focal - (use_focal.varValue * num_bouquets),
        "leftover_foundation": num_foundation - (use_foundation.varValue * num_bouquets),
        "leftover_filler": num_filler - (use_filler.varValue * num_bouquets),
        "leftover_floater": num_floater - (use_floater.varValue * num_bouquets),
        "leftover_finisher": num_finisher - (use_finisher.varValue * num_bouquets),
        "leftover_foliage": num_foliage - (use_foliage.varValue * num_bouquets),
        "actual_bouquet_retail_price": "{:.2f}".format(
            use_focal.varValue * avg_costs["Focal"] +
            use_foundation.varValue * avg_costs["Foundation"] +
            use_filler.varValue * avg_costs["Filler"] +
            use_floater.varValue * avg_costs["Floater"] +
            use_finisher.varValue * avg_costs["Finisher"] +
            use_foliage.varValue * avg_costs["Foliage"]
        ),
    }

    return optimized_results

# ------------------------------------------------
# Streamlit UI
# ------------------------------------------------
# Preview some of the Excel data
df_preview = pd.read_excel(
    "data/Copy of Bouquet Recipe Master Sheet v5 09.07.2025.xlsx",
    sheet_name="Master Variety List"
)
st.write("Preview of Master Variety List:", df_preview.head())

# User inputs
selected_month = st.selectbox("Select Month", [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

retail_price = st.number_input("Target Price per Bouquet ($)", min_value=0.0, step=0.5)
num_bouquets = st.number_input("Number of Bouquets", min_value=1, step=1)

num_focal = st.number_input("Available Focal Flowers", min_value=0, step=1)
num_foundation = st.number_input("Available Foundation Flowers", min_value=0, step=1)
num_filler = st.number_input("Available Filler Flowers", min_value=0, step=1)
num_floater = st.number_input("Available Floater Flowers", min_value=0, step=1)
num_finisher = st.number_input("Available Finisher Flowers", min_value=0, step=1)
num_foliage = st.number_input("Available Foliage Stems", min_value=0, step=1)

if st.button("Run Optimization"):
    try:
        optimized_results = run_optimization(
            selected_month, retail_price, num_bouquets,
            num_focal, num_foundation, num_filler,
            num_floater, num_finisher, num_foliage
        )

        st.subheader("Bouquet Recipe")
        st.write({
            "Focal Flowers": optimized_results["optimized_use_focal"],
            "Foundation Flowers": optimized_results["optimized_use_foundation"],
            "Filler Flowers": optimized_results["optimized_use_filler"],
            "Floater Flowers": optimized_results["optimized_use_floater"],
            "Finisher Flowers": optimized_results["optimized_use_finisher"],
            "Foliage Stems": optimized_results["optimized_use_foliage"],
        })

        st.subheader("Optimization Results")
        st.write(optimized_results)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

        # just checking whether i can commit changes