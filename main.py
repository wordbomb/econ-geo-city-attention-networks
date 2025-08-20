import json
import importlib
import sys
from pathlib import Path
import os

# Load configuration file
with open("config.json", "r") as f:
    config = json.load(f)

# Main function
def main(country_code="us"):
    country_path = os.path.join(".", country_code)

    # Import each processing module and run with the country_path
    for module_name in [
        # "1_Ranking_Calculation",
        # "2_Regression_Analysis",
        # "3_Community_Detection",
        # "4_Community_Features",
        # "5_CPM",
        # "6_LDA",
        # "7_Economic_Indicators_Calculation",
        # "Appendix"
    ]:
        module = importlib.import_module(module_name)
        module.run(country_path,config[country_code])

if __name__ == "__main__":
    # Specify the country code (e.g., "us", "cn")
    if len(sys.argv) > 1:
        country_code = sys.argv[1]
    else:
        country_code = "cn"  # Default country

    main(country_code)