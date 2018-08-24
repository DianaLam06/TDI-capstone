from __future__ import print_function
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
import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import StringIO

from make_figures import *
from get_TMDB import * 

app = flask.Flask(__name__)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]



@lru_cache()

@app.route('/plot.png')
def plot():
    
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    inputted_string = getitem(args, 'movie_name', ' ')
    result_dict = getAPIdata(inputted_string)
    
    d ={'genre_name':[result_dict['genre'].split(',')], 'certification' : [result_dict['rating'].split(',')]}

    
    X_indiv = pd.DataFrame(d)
    cluster_indiv = km4.predict(X_indiv).item(0)
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    xs = range(3 + cluster_indiv)
    ys = [np.random.randint(1, 50) for x in xs]

    axis.imshow(wordcloud[cluster_indiv])
    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    response = flask.make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/')
def index():

    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    inputted_string = getitem(args, 'movie_name', ' ')
    result_dict = getAPIdata(inputted_string)
    
    d ={'genre_name':[result_dict['genre'].split(',')], 'certification' : [result_dict['rating'].split(',')]}

    
    X_indiv = pd.DataFrame(d)
    cluster_indiv = km4.predict(X_indiv).item(0)
    predict_indiv = logistic_genre_cert_PCA.predict(X_indiv)
    #result_dict['wait_time'] = predict_indiv
    
    
    if datetime.datetime.today().year - result_dict['release_date'].year > 5 :
        result_dict['wait_time'] = 'Movie was released more than 5 years ago, demand should be reasonable'
    elif predict_indiv == 0:
        result_dict['wait_time'] = 'Borrow, expected wait at library less than a year'
    elif predict_indiv == 1:
        result_dict['wait_time'] = 'Buy, expected wait longer than a year'
    else :
        result_dict['wait_time'] = 'No prediction, missing feature information'
   
    result_dict['wait_time'] = cluster_indiv



    # resources = INLINE.render()
    # script, div = components(fig)
    
    html = flask.render_template(
        'embed.html',
        movie_name_nice = inputted_string.title(),
        movie_rating = result_dict['rating'],
        movie_genre = result_dict['genre'],
        movie_production = result_dict['production'],
        movie_poster = result_dict['poster'],
        movie_wait_time = result_dict['wait_time'],
        movie_release_date = result_dict['release_date']
    )
    
    return html

if __name__ == '__main__':
    print(__doc__)
    app.run(port=33507, host = '0.0.0.0')
    
    
    
