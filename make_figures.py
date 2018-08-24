import re
import numpy as np
import pandas as pd
import matplotlib 
from collections import defaultdict, Counter


from sklearn import base
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import  OneHotEncoder

from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

#import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS


book_movie = pd.read_csv("./data/book_movie_full.csv")


data_pre = book_movie[["production_names", "genre_name", "certification",\
                       'num_months_wait', 'simpleTitleBook', 'keyword_name']]


def censor24(num_months):
    if num_months <= 24:
        num_months_wait24 = num_months
    else:
        num_months_wait24 = 24
    return num_months_wait24

def censor12(num_months):
    if num_months <= 12:
        num_months_wait12 = num_months
    else:
        num_months_wait12 = 12
    return num_months_wait12

def makeBinary(num_months):
    return 0 if num_months <=12 else 1
        
        

data_pre.at[:,'num_months_wait24'] = data_pre['num_months_wait'].apply(censor24)
data_pre.at[:,'num_months_wait12'] = data_pre['num_months_wait'].apply(censor12)
#data_pre['binary12'] = data_pre['num_months_wait'].apply(makeBinary)
data_outcome = data_pre.dropna()

#data = data_outcome.drop(labels=['num_months_wait'], axis = 1)
data = data_outcome
binary12 = data_outcome['num_months_wait'].apply(makeBinary)



class ColumnSelectTransformer(base.BaseEstimator, base.TransformerMixin):
    
    def __init__(self, col_names):
        self.col_names = col_names  # We will need these in transform()
       
    def fit(self, X, y = None):
        # This transformer doesn't need to learn anything about the data,
        # so it can just return self without any further processing
        
        return self
    
    def transform(self, X):
        # Return an array with the same number of rows as X and one
        # column for each in self.col_names
        # want to return an array that has the data from the column names fed in
        self.X = X
        
        transform = X[self.col_names]

        return transform
    
class DictEncoder(base.BaseEstimator, base.TransformerMixin):
    
    def fit(self, X, y=None):
        return self
       
    def transform(self, X):
        # inputs X: pd.Series
        # outputs list of dicts
        if len(X) > 1:
            X_series = X.squeeze()
            X_word_list = list( X_series.str.split(','))
            return [{name.strip() : 1 for name in lists_ if name is not ""} \
                  for lists_ in X_word_list ]
        
        elif len(X) == 1:
            X_word_list = X.squeeze()
            return [{word: 1 for word in X_word_list if word is not ""} ]
        else :
            return 'help'
       
        

genre = Pipeline([
    ('choose_genre', ColumnSelectTransformer(['genre_name'])),
    ('genre_pre', DictEncoder()),
    ('genre', DictVectorizer())
])



# make certification
certification = Pipeline([
    ('choose_certification', ColumnSelectTransformer(['certification'])),
    ('cert_pre', DictEncoder()),
    ('cert', DictVectorizer())
])



cst_key = ColumnSelectTransformer(['keyword_name'])
data_trans = cst_key.fit_transform(data)
de_key = DictEncoder()
de_trans = de_key.fit_transform(data_trans)
dv_key = DictVectorizer()
dv_trans = dv_key.fit_transform(de_trans)

#key_count = dv_key.inverse_transform(de_trans)

keyword_sum = sum((Counter(movie) for movie in de_trans), Counter())
keyword_sum_sort = sorted(keyword_sum.items(), key= lambda x: x[1], reverse = True)[:10]
keyword_topdict =  {your_key: keyword_sum[your_key] for your_key in keyword_sum.keys() if \
               keyword_sum[your_key] > 2}

class toplist(base.BaseEstimator, base.TransformerMixin):
    def __init__(self, top):
        self.top = top
    
    def fit(self, X, y=None):
        return self
       
    def transform(self, X):
        # inputs X: list of dictionaries
        # outputs: list of dictionaries where keys are in the list of top entries (top)
        return [ { your_key: indiv.get(your_key, 0) for your_key in self.top.keys() } \
                  for indiv in X ]

keyword = Pipeline([
    ('get_key', ColumnSelectTransformer(['keyword_name'])),
    ('key_encoder', DictEncoder()),
    ('key_filter', toplist(keyword_topdict)),
    ('key_vect', DictVectorizer())
])

genre_cert = FeatureUnion([
    ('genre', genre),
    ('certification', certification),
])

# go with this for final model, C is different from the best params

logistic_genre_cert_PCA = Pipeline([
    ('genre_cert', genre_cert),
    ('svd', TruncatedSVD(n_components = 2)),
    ('logistic', LogisticRegression(C=0.1))
    
])

logistic_genre_cert_PCA.fit(data, binary12)


km4 = Pipeline([
    ('genre_cert', genre_cert),
    ('svd', TruncatedSVD(n_components = 2)),  
    ('kmeans', KMeans(n_clusters=4))
])


km4.fit(data)


data.loc[:,'binary12'] = data['num_months_wait'].apply(makeBinary)

data_check = data[data['genre_name'].notnull() == True].reset_index()

# get groups
km4_check = pd.DataFrame(data = km4.fit_predict(data_check))\
.rename(columns = {0: 'cluster4'})


km4 = Pipeline([
    ('genre_cert', genre_cert),
    ('svd', TruncatedSVD(n_components = 2)),  
    ('kmeans', KMeans(n_clusters=4))
])


km4.fit(data)


data_all = pd.merge(data_check, km4_check, left_index = True, right_index = True)

cluster = [ data_all[data_all['cluster4'] == i]['keyword_name'] for i in range(4)]
comment_words = [' '.join(cluster[i]).replace('based', '').replace('novel', '')\
                 .replace('young adult', '').replace(',', '') for i in range(4)]

stopwords = set(STOPWORDS)

wordcloud = [WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(comment_words[i]) for i in range(4)]


'''
matplotlib.pyplot.figure(figsize = (8, 8), facecolor = None)
matplotlib.pyplot.imshow(wordcloud[cluster_indiv])
matplotlib.pyplot.axis("off")
matplotlib.pyplot.tight_layout(pad = 0)
 

data_indiv = data_all[data_all['cluster4'] == cluster_indiv]

data_indiv['num_months_wait12'].hist( normed = True)
'''