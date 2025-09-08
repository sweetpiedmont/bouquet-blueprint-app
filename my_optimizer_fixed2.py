# try making the objective function the minimization of the bouquet price

import pulp
from scipy.optimize import minimize
import pandas as pd
from datetime import datetime

# Specify the path to the CBC solver executable
pulp.CBC_CMD = "/usr/local/bin/cbc"  # Use the actual path you obtained

# Define the run_optimization function that takes input parameters
def run_optimization(selected_month, retail_price, num_bouquets, num_focal, num_foundation, num_filler, num_floater, num_finisher, num_foliage):

# Example: Access the selected_month, retail_price, and other input parameters
    print(f"Received Selected Month in Optimizer: {selected_month}")
    print(f"Retail Price in Optimizer: {retail_price}")
    print(f"Number of Bouquets in Optimizer: {num_bouquets}")
    print(f"Number of Focal Flowers in Optimizer: {num_focal}")
    print(f"Number of Foundation Flowers in Optimizer: {num_foundation}")
    print(f"Number of Filler Flowers in Optimizer: {num_filler}")
    print(f"Number of Floater Flowers in Optimizer: {num_floater}")
    print(f"Number of Finisher Flowers in Optimizer: {num_finisher}")
    print(f"Number of Foliage Stems in Optimizer: {num_foliage}")

# Load  CSV data into a pandas DataFrame
# CSV file is named "Python-Master-Variety-List.csv" and has columns "Flower", "FlowerType", "RetailCostPerStem", and "Season"
    data = pd.read_csv("/Users/sharon/Documents/Sweet Piedmont/Offerings/Bouquet Recipes/Bouquet Recipe App/Python-Master-Variety-List.csv")

# Clean the "RetailCostPerStem" column by removing non-numeric characters and converting to numeric
    data["RetailCostPerStem"] = data["RetailCostPerStem"].str.replace('[^\d.]', '', regex=True).astype(float)

# Assuming 'data' is your DataFrame
    data['Season'] = data['Season'].str.strip()
    data['FlowerType'] = data['FlowerType'].str.strip()

# Step 3: Data Preprocessing

# Define a dictionary to map months to seasons
    month_to_season = {
        'January': 'Winter',
        'February': 'Winter',
        'March': 'Early Spring',
        'April': 'Early Spring',
        'May': 'Late Spring',
        'June': 'Late Spring',
        'July': 'Summer',
        'August': 'Summer',
        'September': 'Fall',
        'October': 'Fall',
        'November': 'Winter',
        'December': 'Winter',
}

# Map selected_month to the corresponding season
    selected_season = month_to_season.get(selected_month, 'Unknown Season')

#Create a price range around the user's selected price to provide the optimizer some flexibility
# Define the price range as $0.50 below and $1.00 above the user-provided retail price
    price_range_lower = retail_price - .5
    price_range_upper = retail_price + 1.0

# Define the flower types
    selected_flower_type = ["Focal", "Foundation", "Filler", "Floater", "Finisher", "Foliage"]

# Define the total number of each flower type available (user input)
    total_focal_available = num_focal
    total_foundation_available = num_foundation
    total_filler_available = num_filler
    total_floater_available = num_floater
    total_finisher_available = num_finisher
    total_foliage_available = num_foliage

# Define the total number of bouquets desired (user input)
    total_bouquets_desired = ['num_bouquets']

# Filter the data based on the specified season and flower type
    filtered_data = data[(data['Season'] == selected_season) & (data['FlowerType'].isin(selected_flower_type))]

# Calculate the average retail cost for each flower type
    average_retail_costs = filtered_data.groupby('FlowerType')['RetailCostPerStem'].mean().to_dict()

# Access the average retail cost for each flower type
    average_retail_cost_focal = average_retail_costs.get('Focal', 0.0)
    average_retail_cost_foundation = average_retail_costs.get('Foundation', 0.0)
    average_retail_cost_filler = average_retail_costs.get('Filler', 0.0)
    average_retail_cost_floater = average_retail_costs.get('Floater', 0.0)
    average_retail_cost_finisher = average_retail_costs.get('Finisher', 0.0)
    average_retail_cost_foliage = average_retail_costs.get('Foliage', 0.0)

    print("Unique Seasons in Data:", data['Season'].unique())
    print("Unique Flower Types in Data:", data['FlowerType'].unique())

    retail_price = float(retail_price)

# Define base upper bounds for each flower type.  Assumes $35 bouquet.
    if selected_season == 'Late Spring':
        base_upper_bound_focal = 1
    else:
        base_upper_bound_focal = 3
        base_upper_bound_foundation = 20
        base_upper_bound_filler = 2
        base_upper_bound_floater = 3
        base_upper_bound_finisher = 2
        base_upper_bound_foliage = 2

# Calculate adjusted upper bounds for each flower type, taking into account the bouquet price
    adjusted_upper_bound_focal = round(base_upper_bound_focal * (retail_price / 35))
    adjusted_upper_bound_foundation = round(base_upper_bound_foundation * (retail_price / 35))
    adjusted_upper_bound_filler = round(base_upper_bound_filler * (retail_price / 35))
    adjusted_upper_bound_floater = round(base_upper_bound_floater * (retail_price / 35))
    adjusted_upper_bound_finisher = round(base_upper_bound_finisher * (retail_price / 35))
    adjusted_upper_bound_foliage = round(base_upper_bound_foliage * (retail_price / 35))

# Create a PuLP model
    model = pulp.LpProblem("Bouquet_Optimization", pulp.LpMinimize)

# Create PuLP variables with adjusted upper bounds for each flower type
    use_focal = pulp.LpVariable("use_focal", lowBound=1, upBound=adjusted_upper_bound_focal, cat="Integer")
    use_foundation = pulp.LpVariable("use_foundation", lowBound=3, upBound=adjusted_upper_bound_foundation, cat="Integer")
    use_filler = pulp.LpVariable("use_filler", lowBound=1, upBound=adjusted_upper_bound_filler, cat="Integer")
    use_floater = pulp.LpVariable("use_floater", lowBound=2, upBound=adjusted_upper_bound_floater, cat="Integer")
    use_finisher = pulp.LpVariable("use_finisher", lowBound=1, upBound=adjusted_upper_bound_finisher, cat="Integer")
    use_foliage = pulp.LpVariable("use_foliage", lowBound=2, upBound=adjusted_upper_bound_foliage, cat="Integer")

# Define the variable for the total cost of the bouquet
    total_cost = (
        use_focal * average_retail_cost_focal +  # Cost of focal flowers
        use_foundation * average_retail_cost_foundation +  # Cost of foundation flowers
        use_filler * average_retail_cost_filler +  # Cost of filler flowers
        use_floater * average_retail_cost_floater +  # Cost of floater flowers
        use_finisher * average_retail_cost_finisher +  # Cost of finisher flowers
        use_foliage * average_retail_cost_foliage  # Cost of foliage flowers
    )

# Access num_bouquets from user_input
    num_bouquets = int(num_bouquets)

# Set up constraints to ensure that the total number of each type of flower doesn't exceed the total number available
    model += use_focal * num_bouquets <= total_focal_available
    model += use_foundation * num_bouquets <= total_foundation_available
    model += use_filler * num_bouquets <= total_filler_available
    model += use_floater * num_bouquets <= total_floater_available
    model += use_finisher * num_bouquets <= total_finisher_available
    model += use_foliage * num_bouquets <= total_foliage_available

# Add a constraint to ensure the total cost is within the lower and upper bounds
    model += (total_cost >= price_range_lower, "PriceLowerBound")
    model += (total_cost <= price_range_upper, "PriceUpperBound")

# Step 5: Bouquet Optimization Algorithm

# Define the objective function to minimize the total bouquet cost
    model += total_cost  # Minimize the negative value to maximize

# Step 6: Bouquet Recipe Generation
# Generate the bouquet recipe based on optimization results.
# Solve the optimization problem
    model.solve()

# Access the optimized values of decision variables
    optimized_use_focal = use_focal.varValue
    optimized_use_foundation = use_foundation.varValue
    optimized_use_filler = use_filler.varValue
    optimized_use_floater = use_floater.varValue
    optimized_use_finisher = use_finisher.varValue
    optimized_use_foliage = use_foliage.varValue

# Define leftover flowers for each flower type
    leftover_focal = num_focal - (optimized_use_focal * num_bouquets)
    leftover_foundation = num_foundation - (optimized_use_foundation * num_bouquets)
    leftover_filler = num_filler - (optimized_use_filler * num_bouquets)
    leftover_floater = num_floater - (optimized_use_floater * num_bouquets)
    leftover_finisher = num_finisher - (optimized_use_finisher * num_bouquets)
    leftover_foliage = num_foliage - (optimized_use_foliage * num_bouquets)

    actual_bouquet_cost = (
        optimized_use_focal * average_retail_cost_focal +  # Cost of focal flowers
        optimized_use_foundation * average_retail_cost_foundation +  # Cost of foundation flowers
        optimized_use_filler * average_retail_cost_filler +  # Cost of filler flowers
        optimized_use_floater * average_retail_cost_floater +  # Cost of floater flowers
        optimized_use_finisher * average_retail_cost_finisher +  # Cost of finisher flowers
        optimized_use_foliage * average_retail_cost_foliage  # Cost of foliage flowers
    )

# Format the price
    formatted_price = "{:.2f}".format(actual_bouquet_cost)

#print("Actual Bouquet Price $" + formatted_price)

# Step 7: Display the Results
# Return the optimization results as a dictionary
    optimized_results = {
        "selected_month": selected_month,
        "retail_price": retail_price,
        "num_bouquets": num_bouquets,
        "num_focal": num_focal,
        "num_foundation": num_foundation,
        "num_filler": num_filler,
        "num_floater": num_floater,
        "num_finisher": num_finisher,
        "num_foliage": num_foliage,
        "optimized_use_focal": optimized_use_focal,
        "optimized_use_foundation": optimized_use_foundation,
        "optimized_use_filler":  optimized_use_filler,
        "optimized_use_floater": optimized_use_floater,
        "optimized_use_finisher": optimized_use_finisher,
        "optimized_use_foliage": optimized_use_foliage,
        "num_bouquets": num_bouquets,
        "leftover_focal": leftover_focal,
        "leftover_foundation": leftover_foundation,
        "leftover_filler": leftover_filler,
        "leftover_floater": leftover_floater,
        "leftover_finisher": leftover_finisher,
        "leftover_foliage": leftover_foliage,
        "actual_bouquet_retail_price": formatted_price
    }

    print("Optimized Results:", optimized_results)

    return optimized_results
