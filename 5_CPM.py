import pandas as pd
import networkx as nx
import matplotlib.colors as mcolors
import json
import os

def run(country_path, config):
    nodes_file = os.path.join(country_path, 'results', 'city_table_count.xlsx')
    edges_file = os.path.join(country_path, 'results', 'city_relations.xlsx')

    
    nodes = pd.read_excel(nodes_file)
    nodes = nodes[nodes['Degree'] != 0]
    edges = pd.read_excel(edges_file)

    G = nx.Graph()
    G.add_edges_from(edges[['source', 'target']].values)

    cpm_k = config["cpm_k"]
    communities = list(nx.algorithms.community.k_clique_communities(G, cpm_k))

    community_dict = {}
    for i, community in enumerate(communities):
        for node in community:
            community_dict.setdefault(node, []).append(i)

    nodes['Community'] = nodes['id'].map(community_dict).fillna(-1)
    nodes = nodes[nodes['Community'] != -1]
    output_file_CPM_nodes = os.path.join(country_path, 'results', f'city_CPM_k{cpm_k}.xlsx')
    nodes.to_excel(output_file_CPM_nodes, index=False)

    valid_nodes = set(nodes['id'])
    filtered_edges = edges[edges['source'].isin(valid_nodes) & edges['target'].isin(valid_nodes)]
    
    output_file_CPM_edges = os.path.join(country_path, 'results', f'city_CPM_edges_k{cpm_k}.xlsx')
    filtered_edges.to_excel(output_file_CPM_edges, index=False)


    # GM
    def transform_coords(row):
        x, y = row['Longitude'], row['Latitude']
        return pd.Series({'x': x, 'y': y})
    
    all_nodes_file = os.path.join(country_path, 'results', 'city_table_count.xlsx')
    all_nodes = pd.read_excel(all_nodes_file)
    all_nodes = all_nodes[all_nodes['Degree'] != 0]

    all_nodes[['x', 'y']] = all_nodes.apply(transform_coords, axis=1)
    std_x_all = all_nodes['x'].std()
    std_y_all = all_nodes['y'].std()
    Dall = std_x_all * std_y_all


    nodes[['x', 'y']] = nodes.apply(transform_coords, axis=1)
    nodes['Community'] = nodes['Community'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    nodes = nodes[nodes['Community'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)]


    gm_results = []
    for community_id in set([community for sublist in nodes['Community'] for community in sublist]):
        community_nodes = nodes[nodes['Community'].apply(lambda x: community_id in x)]
        std_x_community = community_nodes['x'].std()
        std_y_community = community_nodes['y'].std()
        
        Dpart = std_x_community * std_y_community
        GM = Dpart / Dall if Dall != 0 else 0
        gm_results.append({'Community': community_id, 'GM': GM, 'Size': len(community_nodes)})

    gm_df = pd.DataFrame(gm_results)

    # Calculate total GM and Size
    total_gm = sum((gm_df['Size'] * gm_df['GM']).tolist()) / sum(gm_df['Size'].tolist())
    total_size = sum(gm_df['Size'].tolist())

    # Add the total row
    total_row = pd.DataFrame({'Community': ['all'], 'GM': [total_gm], 'Size': [total_size]})
    gm_df = pd.concat([gm_df, total_row], ignore_index=True)
    
    city_CPM_GM_file = os.path.join(country_path, 'results', f'city_CPM_GM_k{cpm_k}.xlsx')
    gm_df.to_excel(city_CPM_GM_file, index=False)
    print(f"Results have been saved to '{city_CPM_GM_file}'")