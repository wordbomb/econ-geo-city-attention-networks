import numpy as np
import random
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import numpy as np
from scipy.sparse import csgraph
from scipy.cluster.vq import kmeans2
import pandas as pd
import networkx as nx
from networkx.algorithms.community import girvan_newman
from networkx.algorithms.community.quality import modularity
import community as community_louvain
import os

def run(country_path, config):
    # Define paths based on country_path
    nodes_file = os.path.join(country_path, 'results', 'city_table_count.xlsx')
    edges_file = os.path.join(country_path, 'results', 'city_relations.xlsx')
    output_file_LPA = os.path.join(country_path, 'results', 'city_LPA.xlsx')
    output_file_LD = os.path.join(country_path, 'results', 'city_LD.xlsx')
    output_file_Louvain = os.path.join(country_path, 'results', 'city_Louvain.xlsx')
    output_file_GN = os.path.join(country_path, 'results', 'city_GN.xlsx')
    output_Q_values_pdf = os.path.join(country_path, 'results', 'The Q-values of four commonly used community detection algorithms.pdf')
    
    nodes = pd.read_excel(nodes_file)
    nodes = nodes[nodes['mention_count'] != 0]
    edges = pd.read_excel(edges_file)

    G = nx.Graph()

    for index, row in nodes.iterrows():
        G.add_node(row['id'])
    for index, row in edges.iterrows():
        G.add_edge(row['source'], row['target'])
        
    # LPA
    np.random.seed(config['community_detection_seed'])
    random.seed(config['community_detection_seed'])
    communities = list(nx.algorithms.community.label_propagation_communities(G))

    community_dict = {}
    for i, community in enumerate(communities):
        for node in community:
            community_dict[node] = i

    nodes['Community'] = nodes['id'].map(community_dict)
    degree_centrality = nx.degree_centrality(G)
    nodes['Degree Centrality'] = nodes['id'].map(degree_centrality)
    betweenness_centrality = nx.betweenness_centrality(G)
    nodes['Betweenness Centrality'] = nodes['id'].map(betweenness_centrality)
    closeness_centrality = nx.closeness_centrality(G)
    nodes['Closeness Centrality'] = nodes['id'].map(closeness_centrality)
    eigenvector_centrality = nx.eigenvector_centrality(G)
    nodes['Eigenvector Centrality'] = nodes['id'].map(eigenvector_centrality)
    clustering_coefficient = nx.clustering(G)
    nodes['Clustering Coefficient'] = nodes['id'].map(clustering_coefficient)
    community_list = [set(community) for community in communities]

    lpa_modularity_value = nx.algorithms.community.quality.modularity(G, community_list)
    nodes.to_excel(output_file_LPA, index=False)

    # LD
    np.random.seed(config['community_detection_seed'])
    random.seed(config['community_detection_seed'])
    adj_matrix = nx.adjacency_matrix(G).toarray()
    laplacian_matrix = csgraph.laplacian(adj_matrix, normed=True)

    num_clusters = 9
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian_matrix)
    X = eigenvectors[:, :num_clusters]

    centroids, labels = kmeans2(X, num_clusters, minit='random')

    community_dict = {node: labels[i] for i, node in enumerate(G.nodes)}

    communities = [[] for _ in range(num_clusters)]
    for node, community_id in community_dict.items():
        communities[community_id].append(node)

    nodes['Community'] = nodes['id'].map(community_dict)
    degree_centrality = nx.degree_centrality(G)
    nodes['Degree Centrality'] = nodes['id'].map(degree_centrality)
    betweenness_centrality = nx.betweenness_centrality(G)
    nodes['Betweenness Centrality'] = nodes['id'].map(betweenness_centrality)
    closeness_centrality = nx.closeness_centrality(G)
    nodes['Closeness Centrality'] = nodes['id'].map(closeness_centrality)
    eigenvector_centrality = nx.eigenvector_centrality(G)
    nodes['Eigenvector Centrality'] = nodes['id'].map(eigenvector_centrality)
    clustering_coefficient = nx.clustering(G)
    nodes['Clustering Coefficient'] = nodes['id'].map(clustering_coefficient)
    community_sets = [set(community) for community in communities]

    ld_modularity_value = nx.algorithms.community.quality.modularity(G, community_sets)
    nodes.to_excel(output_file_LD, index=False)

    # Louvain
    np.random.seed(config['community_detection_seed'])
    random.seed(config['community_detection_seed'])
    community_dict = community_louvain.best_partition(G)

    nodes['Community'] = nodes['id'].map(community_dict)
    degree_centrality = nx.degree_centrality(G)
    nodes['Degree Centrality'] = nodes['id'].map(degree_centrality)
    betweenness_centrality = nx.betweenness_centrality(G)
    nodes['Betweenness Centrality'] = nodes['id'].map(betweenness_centrality)
    closeness_centrality = nx.closeness_centrality(G)
    nodes['Closeness Centrality'] = nodes['id'].map(closeness_centrality)
    eigenvector_centrality = nx.eigenvector_centrality(G)
    nodes['Eigenvector Centrality'] = nodes['id'].map(eigenvector_centrality)
    clustering_coefficient = nx.clustering(G)
    nodes['Clustering Coefficient'] = nodes['id'].map(clustering_coefficient)
    community_sets = [set(community) for community in communities]


    louvain_modularity_value = community_louvain.modularity(community_dict, G)
    nodes.to_excel(output_file_Louvain, index=False)


    # GN
    np.random.seed(config['community_detection_seed'])
    random.seed(config['community_detection_seed'])
    communities_generator = girvan_newman(G)
    top_level_communities = next(communities_generator)
    communities = [set(community) for community in top_level_communities]

    community_dict = {}
    for i, community in enumerate(communities):
        for node in community:
            community_dict[node] = i 

    nodes['Community'] = nodes['id'].map(community_dict)
    degree_centrality = nx.degree_centrality(G)
    nodes['Degree Centrality'] = nodes['id'].map(degree_centrality)
    betweenness_centrality = nx.betweenness_centrality(G)
    nodes['Betweenness Centrality'] = nodes['id'].map(betweenness_centrality)
    closeness_centrality = nx.closeness_centrality(G)
    nodes['Closeness Centrality'] = nodes['id'].map(closeness_centrality)
    eigenvector_centrality = nx.eigenvector_centrality(G)
    nodes['Eigenvector Centrality'] = nodes['id'].map(eigenvector_centrality)
    clustering_coefficient = nx.clustering(G)
    nodes['Clustering Coefficient'] = nodes['id'].map(clustering_coefficient)
    community_sets = [set(community) for community in communities]

    gn_modularity_value = modularity(G, communities)
    nodes.to_excel(output_file_GN, index=False)


    # output_pdf
    algorithms = ['LPA', 'LD', 'Louvain', 'GN']
    q_values = [lpa_modularity_value, ld_modularity_value, louvain_modularity_value, gn_modularity_value]  

    reference_value = 0.3
    colors = ['#4A0080', '#AA2BEF', '#DA52FF', '#FA8BFF'] 

    plt.figure(figsize=(8, 5))
    plt.grid(False)
    bars = plt.bar(algorithms, q_values, color=colors)

    plt.axhline(y=reference_value, color='m', linestyle='--', linewidth=1.5)

    plt.ylabel('Q-value', fontsize=30)
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)
    plt.ylim(0, 0.55)

    plt.tight_layout()
    plt.savefig(output_Q_values_pdf)