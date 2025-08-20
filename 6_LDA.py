import pandas as pd
import ast
import json
import os
import util as util
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import shutil

def run(country_path, config):
    all_comments_data_file = os.path.join(country_path, 'processed_comments_with_ids.xlsx')
    all_comments_data = pd.read_excel(all_comments_data_file)
    all_comments_data['id'] = all_comments_data['id'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [])
    all_comments_data = all_comments_data.explode('id').reset_index(drop=True)

    cpm_k = config['cpm_k']
    city_data_file = os.path.join(country_path,  f'city_CPM_k{cpm_k}.xlsx')
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

    all_comments_data_file = os.path.join(country_path, 'processed_comments_with_ids.xlsx')
    all_comments_data = pd.read_excel(all_comments_data_file)
    if country_path!="cn":
            all_comments_data['Content_cleaned'] = all_comments_data['Content'].apply(util.extract_plain_text)
            all_comments_data['tokens'] = all_comments_data['Content_cleaned'].apply(util.clean_text)
    if country_path=="cn":
        all_comments_data['tokens'] = all_comments_data['Content'].apply(util.clean_text_cn)

    crc_results = []
    for community_id, group in all_comments_data_exploded.groupby('Community'):

        # community
        dictionary_c, corpus_c, lda_model_c = util.lda_topic_extraction(group)
        texts_c = util.generate_texts_from_corpus(corpus_c, dictionary_c)
        cv_c = util.compute_community_coherence(lda_model_c, texts_c, dictionary_c)

        # random selection
        dictionary_rand, corpus_rand, lda_model_rand = util.lda_topic_extraction(all_comments_data.sample(n=len(group)))
        texts_rand = util.generate_texts_from_corpus(corpus_rand, dictionary_rand)
        cv_rand = util.compute_community_coherence(lda_model_rand, texts_rand, dictionary_rand)

        CRC = cv_c / cv_rand
        crc_results.append({'Community ID': community_id, 'CRC': CRC})
        print(cv_c, cv_rand, CRC)

    # Convert to DataFrame and export to an Excel file
    crc_df = pd.DataFrame(crc_results)

    crc_file = os.path.join(country_path, 'results', f'lda_crc_{country_path}.xlsx')
    crc_df.to_excel(crc_file, index=False)
    print(f"Results have been saved to '{crc_file}'")