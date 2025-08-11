import pandas as pd
import statsmodels.api as sm
import os

def run(country_path, config):
    # Define paths based on country_path
    input_file = os.path.join(country_path, 'results', 'city_table_count.xlsx')
    output_file_num_2_gdp_population = os.path.join(country_path, 'results', 'all_num_2_gdp_population_mention_analysis.xlsx')
    output_file_centrality = os.path.join(country_path, 'results', 'all_degree_betweenness_closeness_centrality_mention_rank_analysis.xlsx')

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

    # Reset results dictionary
    results = {}

    # Regression analysis for centrality ranks
    for variable in ['Degree Centrality Rank', 'Betweenness Centrality Rank', 'Closeness Centrality Rank']:
        X = blr[[variable]]
        X = sm.add_constant(X) 
        model = sm.OLS(blr['mention_count Rank'], X).fit()

        results[variable] = {
            'R-squared': model.rsquared,
            'Coefficient': model.params[variable],
            'P-value': model.pvalues[variable]
        }
    # Prepare output DataFrame for centrality rank analysis
    output_df = blr[['ADM2', 'Degree Centrality Rank', 'Betweenness Centrality Rank', 'Closeness Centrality Rank', 'mention_count Rank']].copy()
    summary_df = pd.DataFrame({
        'ADM2': ['R-squared', 'P-value'],
        'Degree Centrality Rank': [results['Degree Centrality Rank']['R-squared'], results['Degree Centrality Rank']['P-value']],
        'Betweenness Centrality Rank': [results['Betweenness Centrality Rank']['R-squared'], results['Betweenness Centrality Rank']['P-value']],
        'Closeness Centrality Rank': [results['Closeness Centrality Rank']['R-squared'], results['Closeness Centrality Rank']['P-value']],
        'mention_count Rank': ['', '']
    })
    output_df = pd.concat([output_df, summary_df], ignore_index=True)
    output_df.to_excel(output_file_centrality, index=False)
