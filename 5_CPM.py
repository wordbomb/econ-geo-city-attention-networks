import pandas as pd
import networkx as nx
import matplotlib.colors as mcolors
import json
import numpy as np
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

    nodes_file = os.path.join(country_path, 'city_table_count.xlsx')
    edges_file = os.path.join(country_path, 'city_relations.xlsx')

    nodes = pd.read_excel(nodes_file)
    nodes = nodes[nodes['Degree'] != 0].copy()
    edges = pd.read_excel(edges_file)

    G = nx.Graph()
    G.add_edges_from(edges[['source', 'target']].values)

    communities = list(nx.algorithms.community.k_clique_communities(G, cpm_k))

    community_dict = {}
    for i, community in enumerate(communities):
        for node in community:
            community_dict.setdefault(node, []).append(i)

    nodes['Community'] = nodes['id'].map(community_dict).fillna(-1)
    nodes = nodes[nodes['Community'] != -1].copy()

    def transform_coords(row):
        return pd.Series({'x': row['Longitude'], 'y': row['Latitude']})
    nodes[['x','y']] = nodes.apply(transform_coords, axis=1)

    nodes['Community'] = nodes['Community'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    nodes = nodes[nodes['Community'].apply(lambda x: isinstance(x, list) and len(x) > 0)].copy()

    all_nodes = pd.read_excel(nodes_file)
    all_nodes = all_nodes[all_nodes['Degree'] != 0].copy()
    all_nodes[['x','y']] = all_nodes.apply(transform_coords, axis=1)
    all_xy = all_nodes[['x','y']].to_numpy()

    B = 500
    rng = np.random.default_rng(42)

    def disp_xy(xy):
        if xy.shape[0] < 2:
            return 0.0
        std_x = np.std(xy[:,0], ddof=1)
        std_y = np.std(xy[:,1], ddof=1)
        return float(std_x * std_y)

    def random_Dall_same_size(m):
        vals = []
        for _ in range(B):
            idx = rng.choice(all_xy.shape[0], size=m, replace=False)
            vals.append(disp_xy(all_xy[idx,:]))
        return float(np.mean(vals)) if vals else 0.0

    # ======  GM  ======
    gm_results = []
    for community_id in set([c for sublist in nodes['Community'] for c in sublist]):
        comm_nodes = nodes[nodes['Community'].apply(lambda lst: community_id in lst)]
        xy = comm_nodes[['x','y']].to_numpy()
        size = xy.shape[0]

        Dpart = disp_xy(xy)
        Dall_rand = random_Dall_same_size(size)
        GM = (Dpart / Dall_rand) if Dall_rand != 0 else np.nan

        gm_results.append({'Community': community_id, 'GM': GM, 'Size': size})

    gm_df = pd.DataFrame(gm_results)

    valid = gm_df.dropna(subset=['GM'])
    if not valid.empty and valid['Size'].sum() > 0:
        total_gm = float(np.average(valid['GM'], weights=valid['Size']))
    else:
        total_gm = np.nan
    total_size = gm_df['Size'].sum()

    total_row = pd.DataFrame({'Community': ['all'], 'GM': [total_gm], 'Size': [total_size]})
    gm_df = pd.concat([gm_df, total_row], ignore_index=True)

    city_CPM_GM_file = os.path.join(country_path, 'results', f'city_CPM_GM_rand_k{cpm_k}_{country_path}.xlsx')
    gm_df.to_excel(city_CPM_GM_file, index=False)
    print(f"Results have been saved to '{city_CPM_GM_file}'")