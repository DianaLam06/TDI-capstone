from __future__ import print_function
#from tmdb_utilities import *
# need to figure out why atonement, the maze runner, and divergent are not working
# may be multiple responses from first requests.get?

try:
    from functools import lru_cache
except ImportError:
    # Python 2 does stdlib does not have lru_cache so let's just
    # create a dummy decorator to avoid crashing
    print ("WARNING: Cache for this example is available on Python 3 only.")
    def lru_cache():
        def dec(f):
            def _(*args, **kws):
                return f(*args, **kws)
            return _
        return dec

import flask
import pandas as pd
from os.path import dirname, join
import requests
from io import BytesIO
from PIL import Image

import re
import numpy as np
#import matplotlib as plt
import matplotlib
from collections import defaultdict, Counter

from sklearn.model_selection import GridSearchCV
from sklearn import base
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

#import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS

app = flask.Flask(__name__)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

def getMovieID(response):
    '''
    input: response from requests.get, used to get numeric id of movie
    output: MovieID key (int)
    '''
    movie_json = response.json()
    return movie_json['results'][0]['id']



# In[12]:

def getAPIwID(id_num):
    '''
    input: the id number (int) of the move to read into the API to get details
    output: a json with movie details
    
    response_full = requests.get("https://api.themoviedb.org/3/movie/" + str(id_num) + \
                            "?api_key=900a489ed1a09a120f925244bffb3f34&language=en-US&append_to_response=details,keywords,release_dates")
    '''
    response_full = requests.get("https://api.themoviedb.org/3/movie/" + str(id_num) +                             "?api_key=900a489ed1a09a120f925244bffb3f34&language=en-US&append_to_response=details,keywords,videos,release_dates")
    
    return response_full.json()

def getRating(deets):
    '''
    input: deets, a json containing the movie details
    output: dictionary with certification
    '''
   
    
    for item in deets['release_dates']['results']:
        if item.values()[0] == u'US':
            return item.values()[1][1]['certification']
    


def getGenre(deets):
    '''
    input: deets, a json containing movie details
    output: single string with all genres, separated by commas
    ''' 
    genre_list = [ i['name'] for i in deets['genres']]
    genre_string = ", ".join(genre_list)
    
    return genre_string
    
    


# In[9]:


def getProduction(deets):
    '''
    input: deets, a json containing movie details from ID grab
    output: the production companies involved in a string, separated by commas
    '''
    return ", ".join([ i['name'] for i in deets['production_companies']])

    

def getPoster(resp):
    '''
    input: the first API response from search
    output: picture of the movie poster
    '''
    poster_path = resp.json()['results'][0]['poster_path']
    full_path = u"https://image.tmdb.org/t/p/w342/" + poster_path    
    URL = requests.get(full_path)
    img = Image.open(BytesIO(URL.content))
    return full_path




def getAPIdata(string):
    '''
    input: a string, which is a movie name, if input is xxyyzz then output blanks with a non commital picture for poster url
    output: movie details from API in a dict
    '''
    if string == " ":
        rating = " "
        genre = " "
        production = " "
        poster = 'http://4.bp.blogspot.com/--vVGyhWo610/VLcuSaQZROI/AAAAAAAAADg/6mYoDt05hJg/s1600/booksvsmovies.jpg'
        wait_time = " "
       
     
    else:

        string_url = "+".join(string.split())
        response = requests.get("https://api.themoviedb.org/3/search/movie?api_key=900a489ed1a09a120f925244bffb3f34&query=" + string_url)

        id_num_ = getMovieID(response)
        details = getAPIwID(id_num_)

        rating = getRating(details)
        genre = getGenre(details)
        production = getProduction(details)
        poster = getPoster(response)
        wait_time = 6
        
    if string.lower() == "crazy rich asians":
        rating = "PG-13"
        production = "Color Force, SK Global, Warner Bros."
        


    all_details = {}
    
    all_details['rating'] = rating
    all_details['genre'] = genre
    all_details['poster'] = poster
    all_details['production'] = production
    all_details['wait_time'] = wait_time
   
  
    return all_details

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
        
        else:
            X_word_list = X.squeeze()
            return [{word: 1 for word in X_word_list if word is not ""} ]
        
book_movie = pd.read_csv("/data/book_movie_full.csv")


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
outcome = data_outcome['num_months_wait']


outcome24  = outcome.apply(censor24)
outcome12 = outcome.apply(censor12)
binary12 = outcome.apply(makeBinary)

@lru_cache()


@app.route('/')
def index():

    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    inputted_string = getitem(args, 'movie_name', ' ')

    result_dict = getAPIdata(inputted_string)

    # resources = INLINE.render()
    # script, div = components(fig)
    
    html = flask.render_template(
        'embed.html',
        movie_name_nice = inputted_string.title(),
        movie_rating = result_dict['rating'],
        movie_genre = result_dict['genre'],
        movie_production = result_dict['production'],
        movie_poster = result_dict['poster'],
        movie_wait_time = result_dict['wait_time']
        
    )
    
    return html

if __name__ == '__main__':
    print(__doc__)
    app.run(port=33507)
