# Import your optimization code
from flask import Flask, render_template, request

from my_optimizer_fixed2 import run_optimization

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve user input from the form
        selected_month = request.form["selected_month"]
        retail_price = float(request.form["retail_price"])
        num_bouquets = int(request.form["num_bouquets"])
        num_focal = int(request.form["num_focal"])
        num_foundation = int(request.form["num_foundation"])
        num_filler = int(request.form["num_filler"])
        num_floater = int(request.form["num_floater"])
        num_finisher = int(request.form["num_finisher"])
        num_foliage = int(request.form["num_foliage"])

       # Print the variables to the console for debugging
        print(f"Received Selected Month: {selected_month}")
        print(f"Recieved Retail Price: {retail_price}")
        print(f"Recieved Number of Bouquets: {num_bouquets}")
        print(f"Received Available Focal Flowers: {num_focal}")
        print(f"Received Available Foundation Flowers: {num_foundation}")
        print(f"Received Available Filler Flowers: {num_filler}")
        print(f"Received Available Floater Flowers: {num_floater}")
        print(f"Received Available Finisher Flowers: {num_finisher}")
        print(f"Received Available Foliage Stems: {num_foliage}")

    try:
        # Call your optimization code to get the results
        optimized_results = run_optimization(
            selected_month, retail_price, num_bouquets,
            num_focal, num_foundation, num_filler,
            num_floater, num_finisher, num_foliage
        )

        # Extract the optimized values for each flower type
        optimized_use_focal = optimized_results["optimized_use_focal"]
        optimized_use_foundation = optimized_results["optimized_use_foundation"]
        optimized_use_filler = optimized_results["optimized_use_filler"]
        optimized_use_floater = optimized_results["optimized_use_floater"]
        optimized_use_finisher = optimized_results["optimized_use_finisher"]
        optimized_use_foliage = optimized_results["optimized_use_foliage"]

        # Access the values from the optimized_results dictionary
        actual_bouquet_retail_price = optimized_results["actual_bouquet_retail_price"]

        # Construct the bouquet recipe
        bouquet_recipe = {
            "Focal Flowers": optimized_use_focal,
            "Foundation Flowers": optimized_use_foundation,
            "Filler Flowers": optimized_use_filler,
            "Floater Flowers": optimized_use_floater,
            "Finisher Flowers": optimized_use_finisher,
            "Foliage Stems": optimized_use_foliage,
        }

        results = {
            "selected_month": selected_month,
            "retail_price": float(retail_price),
            "num_bouquets": int(num_bouquets),
            "num_focal": int(num_focal),
            "num_foundation": int(num_foundation),
            "num_filler": int(num_filler),
            "num_floater": int(num_floater),
            "num_finisher": int(num_finisher),
            "num_foliage": int(num_foliage),
            "optimized_use_focal": optimized_use_focal,
            "optimized_use_foundation": optimized_use_foundation,
            "optimized_use_filler": optimized_use_filler,
            "optimized_use_floater": optimized_use_floater,
            "optimized_use_finisher": optimized_use_finisher,
            "optimized_use_foliage": optimized_use_foliage,
            "leftover_focal": optimized_results["leftover_focal"],
            "leftover_foundation": optimized_results["leftover_foundation"],
            "leftover_filler": optimized_results["leftover_filler"],
            "leftover_floater": optimized_results["leftover_floater"],
            "leftover_finisher": optimized_results["leftover_finisher"],
            "leftover_foliage": optimized_results["leftover_foliage"],
            "actual_bouquet_retail_price": optimized_results["actual_bouquet_retail_price"],
        }

        # Render the result template with the optimized results
        return render_template("result_template.html", results=results)

    except Exception as e:
            # Log the error to help with debugging
            print(f"An error occurred: {str(e)}")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)