import pandas as pd
import statsmodels.api as sm
import os

def run(country_path, config):
    # Define paths based on country_path
    input_file = os.path.join(country_path, 'results', 'city_table_count.xlsx')
    output_file_num_2_gdp_population = os.path.join(country_path, 'results', 'all_num_2_gdp_population_mention_analysis.xlsx')
    # Load the data
    blr = pd.read_excel(input_file)

    # Results dictionary
    results = {}
    # Regression analysis for GDP and Population Rank
    X = blr[['GDP', 'Population']]
    X = sm.add_constant(X)
    model = sm.OLS(blr['mention_count'], X).fit()
    results['Multiple Regression'] = {
        'R-squared': model.rsquared,
        'GDP P-value': model.pvalues['GDP'],
        'Population P-value': model.pvalues['Population']
    }
        # Prepare output DataFrame for GDP and Population analysis
    output_df = blr[['ADM2', 'GDP', 'Population', 'mention_count']].copy()
    summary_df = pd.DataFrame({
        'ADM2': ['R-squared', 'GDP P-value', 'Population P-value'],
        'GDP': [results['Multiple Regression']['R-squared'], 
                     results['Multiple Regression']['GDP P-value'], ''],
        'Population': ['', '', 
                            results['Multiple Regression']['Population P-value']],
        'mention_count': ['', '', '']
    })
    output_df = pd.concat([output_df, summary_df], ignore_index=True)
    output_df.to_excel(output_file_num_2_gdp_population, index=False)