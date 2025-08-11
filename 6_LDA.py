import pandas as pd
import ast
import json
import os
import util as util
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import shutil

def run(country_path, config):


    lda_models_output_dir = os.path.join(country_path, 'data', 'lda_models')
    if os.path.exists(lda_models_output_dir):
        shutil.rmtree(lda_models_output_dir)
    os.makedirs(lda_models_output_dir)

    all_comments_data_file = os.path.join(country_path, 'data', 'processed_comments_with_ids.xlsx')
    all_comments_data = pd.read_excel(all_comments_data_file)
    all_comments_data['id'] = all_comments_data['id'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [])
    all_comments_data = all_comments_data.explode('id').reset_index(drop=True)

    cpm_k = config['cpm_k']
    city_data_file = os.path.join(country_path, 'results', f'city_CPM_k{cpm_k}.xlsx')
    city_data = pd.read_excel(city_data_file)

    all_comments_data = pd.merge(
        all_comments_data, city_data,
        left_on=['id'],
        right_on=['id'],
        how='left'
    )

    all_comments_data['Community'].fillna(-1, inplace=True)
    all_comments_data = all_comments_data[all_comments_data['Community'] != -1]

    if country_path!="cn":
        all_comments_data['Content_cleaned'] = all_comments_data['Content'].apply(util.extract_plain_text)
        all_comments_data['tokens'] = all_comments_data['Content_cleaned'].apply(util.clean_text)

    if country_path=="cn":
        all_comments_data['tokens'] = all_comments_data['Content'].apply(util.clean_text_cn)
    all_comments_data['Community'] = all_comments_data['Community'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    all_comments_data_exploded = all_comments_data.explode('Community')

    for community_id, group in all_comments_data_exploded.groupby('Community'):
        util.lda_topic_extraction(lda_models_output_dir, group, community_id)


    all_comments_data = pd.read_excel(all_comments_data_file)
    if country_path!="cn":
        all_comments = all_comments_data['Content'].apply(util.extract_plain_text).apply(util.clean_text).tolist()     

    if country_path=="cn":
        all_comments = all_comments_data.drop_duplicates(subset=['user ID', 'Content'], keep='last')
        all_comments = all_comments['Content'].apply(util.clean_text_cn).tolist()
    util.lda_global_topic_extraction(lda_models_output_dir, all_comments)

    # Load global model data and LDA models
    global_model_data, all_lda_models = util.load_all_lda_models(lda_models_output_dir)

    global_texts = util.generate_texts_from_corpus(global_model_data['corpus'], global_model_data['dictionary'])
    global_coherence = util.compute_community_coherence(global_model_data['lda_model'], global_texts, global_model_data['dictionary'])
    print("Global Coherence:", global_coherence)

    # Calculate CRC for each community

    crc_results = []
    for community_id, model_data in all_lda_models.items():
        lda_model = model_data['lda_model']
        dictionary = model_data['dictionary']
        corpus = model_data['corpus']
        texts = util.generate_texts_from_corpus(corpus, dictionary)
        cv = util.compute_community_coherence(lda_model, texts, dictionary)
        CRC = cv/global_coherence
        # Append the results to the list
        crc_results.append({'Community ID': community_id, 'CRC': CRC})
        print(cv,CRC)

    # Convert to DataFrame and export to an Excel file
    crc_df = pd.DataFrame(crc_results)

    crc_file = os.path.join(country_path, 'results', 'lda_crc.xlsx')
    crc_df.to_excel(crc_file, index=False)
    print(f"Results have been saved to '{crc_file}'")