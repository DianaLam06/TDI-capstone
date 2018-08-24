from __future__ import print_function
from make_figures import *
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
        genre_html = " "
        production = " "
        poster = 'http://4.bp.blogspot.com/--vVGyhWo610/VLcuSaQZROI/AAAAAAAAADg/6mYoDt05hJg/s1600/booksvsmovies.jpg'
        wait_time = " "
       
     
    else:

        string_url = "+".join(string.split())
        response = requests.get("https://api.themoviedb.org/3/search/movie?api_key=900a489ed1a09a120f925244bffb3f34&query=" + string_url)

        id_num_ = getMovieID(response)
        details = getAPIwID(id_num_)

        rating = getRating(details)
        genre_html = getGenre(details)
        production = getProduction(details)
        poster = getPoster(response)
        wait_time = 6
        
    if string.lower() == "crazy rich asians":
        rating = "PG-13"
        production = "Color Force, SK Global, Warner Bros."
        


    all_details = {}
    
    all_details['rating'] = rating
    all_details['genre'] = genre_html
    all_details['poster'] = poster
    all_details['production'] = production
    all_details['wait_time'] = wait_time
   
  
    return all_details


@lru_cache()


@app.route('/')
def index():

    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    inputted_string = getitem(args, 'movie_name', ' ')
    result_dict = getAPIdata(inputted_string)
    
    d ={'genre_name':[result_dict['genre']], 'certification' : [result_dict['rating']]}
    X_indiv = pd.DataFrame(d)
    cluster_indiv = km4.predict(X_indiv).item(0)
    if cluster_indiv == 0:
        result_dict['wait_time'] = 'Borrow, expected wait at library less than a year'
    else:
        result_dict['wait_time'] = 'Buy, expected wait longer than a year'

    predict_indiv = logistic_genre_cert_PCA.predict(X_indiv).item(0)

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
