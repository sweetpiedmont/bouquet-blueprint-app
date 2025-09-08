def run_optimization(selected_month, retail_price, num_bouquets,
                     num_focal, num_foundation, num_filler,
                     num_floater, num_finisher, num_foliage):

    # Load Excel Master Variety List
    data = pd.read_excel(
        "data/Copy of Bouquet Recipe Master Sheet v5 09.07.2025.xlsx",
        sheet_name="Master Variety List"
    )

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
        use_fol