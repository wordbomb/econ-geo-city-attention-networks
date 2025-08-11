
import pandas as pd
from bs4 import BeautifulSoup
import ast
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim import corpora
from gensim.models import LdaModel
import nltk
import json
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from gensim import matutils
from nltk import pos_tag
import jieba
from gensim.models import CoherenceModel

def extract_plain_text(html_content):
    if pd.isna(html_content):
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()


def clean_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english')).union({'day','thing','days', 'time','times','get', 'gets', 'year', 'years','week','weeks','people','something','morning', 'night','minute','minutes','nights', 'thing', 'way','weekend','weekends','return','returns', 'hi', 'hello', 'thank','thanks','try', 'trys', 
    'thought', 'month', 'months', 'dinner', 'lunch', 'area', 'place','places', 'plan', 'hotel', 'tour', 'trip', 'test', 'site', 'anyone', 'advance','place','road','see', 'trip','option','options','request','advice','visit','service','please','need','needs','travel','travels',
    'city', 'advice', 'use','uses','hour','hours','transport','transports','lines','line','travel','travels','post','posts','author','authors','help',
    'helps','arrival','arrivals','test','tests','question','questions','afternoon','thought','thoughts','suggestion','suggestions','bit','bits','recommendation','recommendations','question','questions','information','informations','stay','stays'})  # 添加自定义词
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    tagged_tokens = pos_tag(filtered_tokens)
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word, tag in tagged_tokens]
    return lemmatized_tokens


def clean_text_cn(text):
    with open('stopwords.txt', 'r', encoding='utf-8') as f:
        stop_words = set(f.read().splitlines())
    tokens = jieba.cut(text)
    filtered_tokens = [word for word in tokens if word not in stop_words and word.strip() != '']
    return filtered_tokens

def save_lda_model(output_dir, community_id, lda_model, dictionary, corpus):
    lda_model.save(os.path.join(output_dir, f"community_{community_id}_lda.model"))
    dictionary.save(os.path.join(output_dir, f"community_{community_id}_dictionary.dict"))
    corpora.MmCorpus.serialize(os.path.join(output_dir, f"community_{community_id}_corpus.mm"), corpus)

def lda_topic_extraction(output_dir, group, community_id):
    processed_docs = group['tokens'].tolist()
    if processed_docs:
        dictionary = corpora.Dictionary(processed_docs)
        # dictionary.filter_extremes(no_below=2, no_above=0.5)
        corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

        lda_model = LdaModel(corpus, id2word=dictionary, passes=50)

        save_lda_model(output_dir,community_id, lda_model, dictionary, corpus)

def lda_global_topic_extraction(output_dir, global_processed_docs):
    if global_processed_docs:
        global_dictionary = corpora.Dictionary(global_processed_docs)
        # global_dictionary.filter_extremes(no_below=2, no_above=0.5)
        global_corpus = [global_dictionary.doc2bow(doc) for doc in global_processed_docs]

        global_lda_model = LdaModel(global_corpus, id2word=global_dictionary, passes=50)
        save_lda_model(output_dir, 'global', global_lda_model, global_dictionary, global_corpus)


def plot_wordcloud(lda_model, topic_num, community_id):
    words = dict(lda_model.show_topic(topic_num, 50))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(words)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title(f"Word Cloud for Community {community_id}, Max Weight Topic {topic_num}")
    plt.show()

def load_lda_model(output_dir, community_id):
    lda_model = LdaModel.load(os.path.join(output_dir, f"community_{community_id}_lda.model"))
    dictionary = corpora.Dictionary.load(os.path.join(output_dir, f"community_{community_id}_dictionary.dict"))
    corpus = corpora.MmCorpus(os.path.join(output_dir, f"community_{community_id}_corpus.mm"))
    return lda_model, dictionary, corpus

def get_max_weight_topic(lda_model, corpus, community_id):
    topics = matutils.corpus2dense(lda_model[corpus], num_terms=lda_model.num_topics)
    weight = topics.sum(1)
    max_topic = weight.argmax()
    words = lda_model.show_topic(max_topic, 50)
    return dict(words)
    
def load_all_lda_models(output_dir):
    lda_models_dict = {}
    global_model_data = None
    
    for file_name in os.listdir(output_dir):
        if file_name.endswith('_lda.model'):
            community_id = file_name.split('_')[1] if 'community' in file_name else 'global'
            
            lda_model = LdaModel.load(os.path.join(output_dir, f'{file_name}'))
            dictionary = corpora.Dictionary.load(os.path.join(output_dir, f'{file_name.replace("lda.model", "dictionary.dict")}'))
            corpus = corpora.MmCorpus(os.path.join(output_dir, f'{file_name.replace("lda.model", "corpus.mm")}'))
            
            if community_id == 'global':
                global_model_data = {'lda_model': lda_model, 'dictionary': dictionary, 'corpus': corpus}
            else:
                lda_models_dict[community_id] = {'lda_model': lda_model, 'dictionary': dictionary, 'corpus': corpus}
    
    return global_model_data, lda_models_dict

def compute_community_coherence(lda_model, texts, dictionary):
    coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
    return coherence_model_lda.get_coherence()

def generate_texts_from_corpus(corpus, dictionary):
    return [[dictionary[word_id] for word_id, freq in doc] for doc in corpus]