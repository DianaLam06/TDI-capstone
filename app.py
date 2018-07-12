from __future__ import print_function

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

app = flask.Flask(__name__)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]


@lru_cache()


@app.route('/')
def index():

    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    inputted_string = getitem(args, 'movie_name', 'Annihilation')


    # resources = INLINE.render()
    # script, div = components(fig)
    
    html = flask.render_template(
        'embed.html',
        movie_string=inputted_string
    )
    
    return html

if __name__ == '__main__':
    print(__doc__)
    app.run(port=33507)
