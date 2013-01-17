#!/usr/bin/env python

from flask import Flask, Response, request, render_template

import settings
from common import redis

try:
    if os.environ.get('DEBUG'):
        import settings_local as settings
    else:
        import settings_prod as settings
except ImportError:
    import settings

app = Flask(__name__)


@app.route('/')
def index():
    return csv()
    #return render_template('index.html', counts=counts)


@app.route('/csv')
def csv():
    def generate():
        rows = [
        ]
        #for row in rows:
        #    yield ','.join(row) + '\n'
    return Response(generate(), mimetype='text/csv')


if __name__ == '__main__':
    debug = bool(os.environ.get('DEBUG'))
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug, host='0.0.0.0', port=port)
