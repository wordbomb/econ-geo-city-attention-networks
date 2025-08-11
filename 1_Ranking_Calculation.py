import pandas as pd
import matplotlib.pyplot as plt
import ast

def run(country_path, config):
    # Load data and preprocess
    if config['country'] == 'cn':
      data = pd.read_excel(f'{country_path}/data/comment_data_filter.xlsx')
      city_table_df = pd.read_excel(f'{country_path}/results/city_table_count.xlsx')
    if config['country'] == 'uk':
      data = pd.read_excel(f'{country_path}/data/processed_comments_with_ids.xlsx')
      data['id'] = data['id'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [])
      data = data.explode('id').reset_index(drop=True)
      city_table_df = pd.read_excel(f'{country_path}/results/city_table_count.xlsx')
      
    if config['country'] == 'us':
      data = pd.read_excel(f'{country_path}/data/processed_comments_with_ids.xlsx')
      data['id'] = data['id'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [])
      data = data.explode('id').reset_index(drop=True)
      city_table_df = pd.read_excel(f'{country_path}/results/city_table_count.xlsx')
      ak_hi_ids = [2013,2016,2020,2050,2060,2063,2066,2068,2070,2090,2100,2105,2110,2122,2130,2150,2158,2164,2170,2180,2185,2188,2195,2198,2220,2230,2240,2275,2282,2290,15001,15003,15007,15901]
      data = data[~data['id'].isin(ak_hi_ids)]

    county_name_map = dict(zip(city_table_df['id'], city_table_df['ADM2']))

    # Generate monthly data
    data['year_month'] = data['Date Created'].dt.to_period('M')
    city_monthly_data = data.groupby(['id', 'year_month']).size().reset_index(name='count')

    # Filter top cities by month and determine consistent top cities
    top_cities_by_month = city_monthly_data.groupby('year_month', group_keys=False) \
                          .apply(lambda x: x.nlargest(10, 'count')).reset_index(drop=True)
    consistent_top_cities = top_cities_by_month['id'].value_counts() \
                          [lambda x: x == top_cities_by_month['year_month'].nunique()].index
    consistent_top_cities_data = top_cities_by_month[top_cities_by_month['id'].isin(consistent_top_cities)]
    consistent_top_cities_data['rank'] = consistent_top_cities_data.groupby('year_month')['count'] \
                                           .rank(ascending=False, method='min')

    # Create pivot table for ranks and convert to numeric
    pivot_city_ranks = consistent_top_cities_data.pivot(index='year_month', columns='id', values='rank') \
                          .apply(pd.to_numeric, errors='coerce')
    months = pivot_city_ranks.index.astype(str)
    markers = ['o', 'D', 's', '*', '^', 'v', '>', '<', 'p', 'h']

    # Plot setup
    plt.figure(figsize=(10, 6))
    plt.grid(False)

    # Plot each city with a unique marker
    for i, city in enumerate(pivot_city_ranks.columns):
        county_name = county_name_map.get(city, 'Unknown')
        plt.plot(months, pivot_city_ranks[city].values, marker=markers[i % len(markers)], 
                 label=county_name, markersize=15)

    # Customize and save plot
    plt.ylim(0, 11)
    plt.gca().invert_yaxis()
    plt.legend(loc='lower left', ncol=3, fontsize=16)
    plt.yticks(range(1, 10), fontsize=26)
    plt.ylabel('Mentions Rank', fontsize=30)
    plt.xticks(fontsize=26)
    plt.tight_layout()
    plt.savefig(f'{country_path}/results/Mentions Rank.pdf')

    # Export top cities data
    city_table_df[city_table_df['id'].isin(consistent_top_cities)] \
                 [['ADM2', 'GDP Rank', 'GDP', 'Population Rank', 'Population', 'Degree Centrality Rank', 'Degree Centrality',
                   'Betweenness Centrality Rank', 'Betweenness Centrality', 'Closeness Centrality Rank', 'Closeness Centrality', 'mention_count Rank', 'mention_count']] \
                 .to_excel(f'{country_path}/results/top_cities_data.xlsx', index=False)
