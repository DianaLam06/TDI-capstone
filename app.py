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
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
import pandas as pd
from os.path import dirname, join
from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select

app = flask.Flask(__name__)

colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}

months = {
    'Jan' : 1,
    'Feb' : 2,
    'Mar' : 3,
    'Apr' : 4,
    'May' : 5,
    'Jun' : 6,
    'Jul' : 7,
    'Aug' : 8,
    'Sep' : 9,
    'Oct' :10,
    'Nov' :11,
    'Dec' :12
    }

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

DATA_DIR = join(dirname(__file__), 'daily')

@lru_cache()
def load_ticker(ticker):
    fname = join(DATA_DIR, 'table_%s.csv' % ticker.lower())
    data = pd.read_csv(fname, header=None, parse_dates=['Date'],
                       names=['Date', 'foo', 'o', 'h', 'l', 'Close', 'v'])
    return data[['Date','Close']]


@app.route('/')
def index():

    # Grab the inputs arguments from the URL
    args = flask.request.args

    # Get all the form arguments in the url with defaults
    color = getitem(args, 'color', 'Black')
    ticker = getitem(args, 'stock', 'AAPL')
    month = getitem(args, 'month', 'Jan')

    stockdata_all = load_ticker(ticker)
    stockdata = stockdata_all[(stockdata_all['Date'].dt.month==months[month]) & (stockdata_all['Date'].dt.year==2000)]
    fig = figure(title=ticker.upper()+" data for 2000", x_axis_type = "datetime")
    fig.line(stockdata['Date'], stockdata['Close'], color=colors[color], line_width=2)

    resources = INLINE.render()

    script, div = components(fig)
    html = flask.render_template(
        'embed.html',
        plot_script=script,
        plot_div=div,
        resources=resources,
        color=color,
        ticker=ticker,
        month=month
    )
    
    return html

if __name__ == '__main__':
    print(__doc__)
    app.run(port=33507)
