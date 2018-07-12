from tmdb_config import API_KEY
import requests
from io import BytesIO
#from PIL import Image

def getMovieID(response):
    '''
    input: response from requests.get, used to get numeric id of movie
    output: MovieID key (int)
    '''
    movie_json = response.json()
    return movie_json['results'][0]['id']

def getAPIwID(id_num):
    '''
    input: the id number (int) of the move to read into the API to get details
    output: a json with movie details
    
    response_full = requests.get("https://api.themoviedb.org/3/movie/" +
                                         str(id_num) + 
                                         "?api_key=" + 
                                         API_KEY + 
                                        "&language=en-US&append_to_response=details,keywords,release_dates")
    '''
    response_full = requests.get("https://api.themoviedb.org/3/movie/" + 
                                        str(id_num) + 
                                        "?api_key=" + 
                                        API_KEY + 
                                        "&language=en-US&append_to_response=details,keywords,videos,release_dates")
    
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
    output: dictionary with genres
    '''
    
    return [ i['name'] for i in deets['genres']]
    
def getProduction(deets):
    '''
    input: deets, a json containing movie details from ID grab
    output: the production companies involved
    '''
    return  [ i['name'] for i in deets['production_companies']]
'''
def getPoster(resp):
   
    input: the first API response from search
    output: picture of the movie poster
   
    poster_path = resp.json()['results'][0]['poster_path']
    full_path = u"https://image.tmdb.org/t/p/w342/" + poster_path    
    URL = requests.get(full_path)
    img = Image.open(BytesIO(URL.content))
    return img    
'''

def getAPIdata(string):
    '''
    input: a string, which is a movie name
    output: movie details from API in a dict
    '''
    string_url = "+".join(string.split())
    response = requests.get("https://api.themoviedb.org/3/search/movie?api_key=" + API_KEY + "&query=" + string_url)
    
    id_num_ = getMovieID(response)
    details = getAPIwID(id_num_)
    
    rating = getRating(details)
    genre = getGenre(details)
    production = getProduction(details)
    #poster = getPoster(response)
    
    all_details = {}
    
    all_details['rating'] = rating
    all_details['genre'] = genre
    #all_details['poster'] = poster
    all_details['production'] = production
    
    return all_details
