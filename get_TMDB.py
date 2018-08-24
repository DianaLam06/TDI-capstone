
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
    try:
        if 'release_dates' in deets.keys():
            for item in deets['release_dates']['results']:
                if item.values()[0] == u'US':
                    for subitem in item.values()[1]:
                        if subitem['certification'] != u'':
                            return subitem['certification']
    except AttributeError:
        return 'No rating found'
    


def getGenre(deets):
    '''
    input: deets, a json containing movie details
    output: single string with all genres, separated by commas
    ''' 
    genre_list = [ i['name'] for i in deets['genres']]
    genre_string = ", ".join(genre_list)
    
    return genre_string
    
    

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

def getReleaseDateWithEmpty(deets):
    '''
    input: json with movie details
    otuput: release date
    '''
    if 'release_dates' in deets.keys() and 'results' in deets['release_dates'].keys():
        for item in deets['release_dates']['results']:
            try:
                if item.values()[0] == u'US':
                    for subitem in item.values()[1]:
                        if subitem['certification'] != u'':

                            s = item.values()[1][0]['release_date']

                            s_short = re.search(u'\d{4}-\d{2}-\d{2}', s).group()
                            t = datetime.datetime.strptime(s_short, u"%Y-%m-%d")
                            return t
            except AttributeError:
                return 'No release date found'


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
        release_date = datetime.datetime.today()
        
       
     
    else:

        string_url = "+".join(string.split())
        response = requests.get("https://api.themoviedb.org/3/search/movie?api_key=900a489ed1a09a120f925244bffb3f34&query=" + string_url)

        id_num_ = getMovieID(response)
        details = getAPIwID(id_num_)

        rating = getRating(details)
        genre_html = getGenre(details)
        production = getProduction(details)
        poster = getPoster(response)
        release_date = getReleaseDateWithEmpty(details)
        
        
    if string.lower() == "crazy rich asians":
        rating = "PG-13"
        production = "Color Force, SK Global, Warner Bros."
        


    all_details = {}
    
    all_details['rating'] = rating
    all_details['genre'] = genre_html
    all_details['poster'] = poster
    all_details['production'] = production
    all_details['release_date'] = release_date
  
    return all_details