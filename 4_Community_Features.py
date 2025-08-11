import pandas as pd
import os
from scipy.stats import linregress
from collections import defaultdict
import statsmodels.api as sm

def run(country_path, config):
    output_file = os.path.join(country_path, 'results', 'gdp_mentions_effectivesize_regression.txt')
    with open(output_file, "w", encoding="utf-8") as file:

        # Analysis 1: GDP vs Mention Count
        Louvain_file = os.path.join(country_path, 'results', 'city_Louvain.xlsx')
        nodes  = pd.read_excel(Louvain_file)

        required_columns = ['Community', 'mention_count', 'GDP']

        grouped = nodes.groupby('Community')[['mention_count', 'GDP']].sum().reset_index()

        output_file_path = os.path.join(country_path, 'data', 'community_aggregated_data.xlsx')
        grouped.to_excel(output_file_path, index=False)

        if len(grouped) < 2:
            print("Not enough communities for regression analysis.")
        else:
            gdp = grouped['GDP']
            mentions = grouped['mention_count']

            slope, intercept, r_value, p_value, std_err = linregress(gdp, mentions)

            r_squared = r_value ** 2
            file.write("GDP vs Mention Count Regression Analysis:\n")
            file.write(f"Number of samples (communities): {len(grouped)}\n")
            file.write(f"Regression equation: mention_count = {slope:.6f} * GDP + {intercept:.6f}\n")
            file.write(f"R-squared: {r_squared:.6f}\n")
            file.write(f"P-value: {p_value:.6f}")
            file.write("\n" + "="*40 + "\n\n")


        nodes = nodes[nodes['Degree'] != 0]
        
        # Analysis 2: GDP vs Effective Size
        edges_file = os.path.join(country_path, 'results', 'city_relations.xlsx')
        relation_df = pd.read_excel(edges_file)
        neighbors = defaultdict(set)
        for _, row in relation_df.iterrows():
            source = row['source']
            target = row['target']
            neighbors[source].add(target)
            neighbors[target].add(source)

        def count_links_within_neighbors(city_id):
            neighbor_list = neighbors[city_id]
            if len(neighbor_list) < 2:
                return 0
            internal_links = 0
            for neighbor in neighbor_list:
                for other_neighbor in neighbor_list:
                    if neighbor != other_neighbor and (neighbor in neighbors[other_neighbor]):
                        internal_links += 1
            return internal_links // 2

        effective_sizes = {}
        for city_id in nodes['id']:
            N = len(neighbors[city_id])
            L = count_links_within_neighbors(city_id)
            if N > 0:
                ES = N - (2 * L / N)
            else:
                ES = 0 
            effective_sizes[city_id] = ES

        nodes['Effective Size'] = nodes['id'].map(effective_sizes)

        X = nodes['GDP']
        y = nodes['Effective Size']
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        
        # Write results of GDP vs Effective Size
        file.write("GDP vs Effective Size Regression Analysis:\n")
        file.write(f"R-squared: {model.rsquared}\n")
        file.write(f"Coefficient: {model.params['GDP']}\n")
        file.write(f"P-value: {model.pvalues['GDP']}\n")
        file.write("\n" + "="*40 + "\n\n")

    print(f"All analysis results have been saved to {output_file}")