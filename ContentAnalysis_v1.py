import os
import numpy as np
import pandas as pd
import gensim 
import pyLDAvis.gensim
import nltk
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm
from operator import itemgetter
from wordcloud import WordCloud
import string
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

punct = list(string.punctuation)
stop_words = list(nltk.corpus.stopwords.words('english'))
patent_stops = 'application, user, method, apparatus, system, device, a, has, such, accordance, have, suitable, according, having, than, all, herein, that, also, however, the, an, if, their, and, in, then, another, into, there, are, invention, thereby, as, is, therefore, at, it, thereof, be, its, thereto, because, means, these, been, not, they, being, now, this, by, of, those, claim, on, thus, comprises, onto, to, corresponding, or, use, could, other, various, described, particularly, was, desired, preferably, were, do, preferred, what, does, present, when, each, provide, where, embodiment, provided, whereby, fig, provides, wherein, figs, relatively, which, for, respectively, while, from, said, who, further, should, will, generally, since, with, had, some, would, first, second, third, fourth, fifth, sixth, seventh, eighth, ninth, tenth, eleventh, twelveth, thtiteenth, least, field, using, applying, based'
patent_stops = patent_stops.split(', ')
global stop
stop = list(set(patent_stops + stop_words + punct))

def normalize_corpus(patents):
    # Removing stopwords and patent stopwords by USPTO
    wtk = nltk.tokenize.RegexpTokenizer(r'\w+')
    wnl = WordNetLemmatizer()
    # patent_stops = 'a, has, such, accordance, have, suitable, according, having, than, all, herein, that, also, however, the, an, if, their, and, in, then, another, into, there, are, invention, thereby, as, is, therefore, at, it, thereof, be, its, thereto, because, means, these, been, not, they, being, now, this, by, of, those, claim, on, thus, comprises, onto, to, corresponding, or, use, could, other, various, described, particularly, was, desired, preferably, were, do, preferred, what, does, present, when, each, provide, where, embodiment, provided, whereby, fig, provides, wherein, figs, relatively, which, for, respectively, while, from, said, who, further, should, will, generally, since, with, had, some, would, first, second, third, fourth, fifth, sixth, seventh, eighth, ninth, tenth, eleventh, twelveth, thtiteenth, least, field, using, applying, based'
    # patent_stops = patent_stops.split(', ')
    # stop = list(set(patent_stops + stop_words + punct))
    norm_papers = []
    for text in patents:
        text = text.lower()
        text_tokens = [token.strip() for token in wtk.tokenize(text)]
        text_tokens = [wnl.lemmatize(token) for token in text_tokens if not text.isnumeric()]
        text_tokens = [token for token in text_tokens if len(token) > 1]
        text_tokens = [token for token in text_tokens if token not in stop]
        text_tokens = list(filter(None, text_tokens))
        if text_tokens:
            norm_papers.append(text_tokens)
    return norm_papers

def topic_model_coherence_generator(corpus, texts, dictionary, start_topic_count = 2, end_topic_count = 10, step = 1, cpus = 1, topn_words_per_topic = 30, lda_iterations = 500):
    models = []
    coherence_scores = []
    for topic_nums in tqdm(range(start_topic_count, end_topic_count + 1, step)):
        lda_model = gensim.models.LdaMulticore(corpus = corpus, num_topics = topic_nums, id2word = dictionary, iterations = lda_iterations, workers = cpus)
        cv_coherence_model_lda = gensim.models.CoherenceModel(model = lda_model, corpus = corpus, texts = texts, dictionary = dictionary, coherence = 'c_v')
        coherence_score = cv_coherence_model_lda.get_coherence()
        coherence_scores.append(coherence_score)
        models.append(lda_model)
    return models, coherence_scores

#def topics_vis_plot(best_lda_model, bow_corpus, dictionary):
#    pyLDAvis.gensim.prepare(best_lda_model, bow_corpus, dictionary)

def topics(filename, claims_abstract = True, min_count_keywords = 20, threshold_keywords = 20, min_topics = 2, max_topics = 10, cpus = 1, topn_words_per_topic = 30, lda_iterations = 500):
    
    df = pd.read_csv(filename)
    
    titles = df['title']
    if claims_abstract:
        abstract = df['abstract']
        claims = df['claims']
        text_data = []
        for i in range(len(titles)):
            text = str(titles[i]) + str(abstract[i]) + str(claims[i])
            text_data.append(text)
    else:
        text_data = []
        for i in range(len(titles)):
            text = str(titles[i])
            text_data.append(text)

    # Text wrangling and normalization
    norm_papers = normalize_corpus(text_data)

    # Keyphrase Extaction / Feature Engineering
    # Ways to generate phrases with influential bi-grams and remove some terms that may not be useful before feature engineering
    bigram = gensim.models.Phrases(norm_papers, min_count = min_count_keywords, threshold = threshold_keywords, delimiter = b'_') # higher threshold fewer words
    bigram_model = gensim.models.phrases.Phraser(bigram)

    # building vocabulary and from the corpus and filter out word with count < 20 and count > 60%
    norm_corpus_bigrams = [bigram_model[doc] for doc in norm_papers]
    dictionary = gensim.corpora.Dictionary(norm_corpus_bigrams)

    # Text Representation (BOW)
    bow_corpus = [dictionary.doc2bow(text) for text in norm_corpus_bigrams]

    # Topic Modeling (LDA) with hyperparameter tuning to find optimal topics
    lda_models, coherence_scores = topic_model_coherence_generator(corpus = bow_corpus, texts = norm_corpus_bigrams, dictionary = dictionary, start_topic_count = min_topics, end_topic_count = max_topics, step = 1, cpus = cpus, lda_iterations = lda_iterations)

    coherence_df = pd.DataFrame({'Number of Topics':range(min_topics, max_topics + 1, 1), 'Coherence Score':np.round(coherence_scores, 4)})
    coherence_df.sort_values(by = ['Coherence Score'], ascending = False)

    # getting the best LDA model with maximum coherence score
    best_model_idx = coherence_df[coherence_df['Coherence Score'] == max(coherence_df['Coherence Score'])].index[0]
    best_lda_model = lda_models[best_model_idx]

    topics = [[(term, round(wt, 3)) for term, wt in best_lda_model.show_topic(n, topn = topn_words_per_topic)] for n in range(0, best_lda_model.num_topics)]
    topics_df = pd.DataFrame([', '.join([term for term, wt in topic]) for topic in topics], columns = ['Terms per Topics'], index = ['Topic'+str(t) for t in range(1, best_lda_model.num_topics + 1)])

    lda_corpus = best_lda_model[bow_corpus] 
    topics_distribution = {}
    for i in lda_corpus:
        res = max(i, key = itemgetter(1))[0]
        res = res + 1
        if res in topics_distribution.keys():
            topics_distribution[res] += 1
        else:
            topics_distribution[res] = 1

    num_topics = best_lda_model.num_topics
    threshold_low = (len(df) / num_topics)/ 1.3
    threshold_high = (len(df) / num_topics)*1.5
    hotspots = []
    vacuume = []
    for i in topics_distribution.keys():
        if topics_distribution[i] >= threshold_high:
            hotspots.append(i)
        elif topics_distribution[i] < threshold_low:
            vacuume.append(i)   

    # Hotspots
    for i in sorted(hotspots):
            words = topics_df.iloc[i-1][0].split(', ')
            print(f'Hotspot for Topic {i}: ')
            comment_words = '' 
            comment_words += " ".join(words)+" "
            wordcloud = WordCloud(max_font_size=50, width = 700, height = 400, 
                    background_color ='black', 
                    stopwords = stop, 
                    min_font_size = 10).generate(comment_words)
            plt.figure(figsize = (4, 4), facecolor = 'white') 
            plt.imshow(wordcloud) 
            plt.axis("off") 
            plt.tight_layout(pad = 0) 
            plt.show() 

    # Vacuum
    for i in sorted(vacuume):
        words = topics_df.iloc[i-1][0].split(', ')
        print(f'Vacuum for Topic {i}: ')
        comment_words = '' 
        comment_words += " ".join(words)+" "
        wordcloud = WordCloud(max_font_size=50, width = 700, height = 400, 
                    background_color ='black', 
                    stopwords = stop, 
                    min_font_size = 10).generate(comment_words)
        plt.figure(figsize = (4, 4), facecolor = 'white') 
        plt.imshow(wordcloud) 
        plt.axis("off") 
        plt.tight_layout(pad = 0) 
        plt.show()

    #if topic_vis:
    #    pyLDAvis.gensim.prepare(best_lda_model, bow_corpus, dictionary)
    return best_lda_model, bow_corpus, dictionary