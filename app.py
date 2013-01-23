#!/usr/bin/env python

import os

from flask import Flask, Response, render_template

import settings
from common import redis
from tweets import moods, totals

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
    return html_exact()


@app.route('/html/exact')
def html_exact():
    return render_template('report.html', **_generate_html('exact'))


@app.route('/html/fuzzy')
def html_fuzzy():
    return render_template('report.html', **_generate_html('fuzzy'))


def _generate_html(precision):
    runs = []

    # Get sorted set in descending order by date.
    stored_runs = redis.zrevrange('runs', 0, -1, 1)

    for run_timestamp, run_key in stored_runs:
        # This is the value of the run which we key off of (e.g., 20130116233651).
        run_key = str(int(run_key))

        run = {'timestamp': run_timestamp, 'counts': []}

        for mood in moods:
            try:
                # Get the string of the mood count.
                count = redis.get('runs:%s:moods:%s:%s'
                                  % (run_key, precision, mood))
            except:
                # Maybe this key is not a set - or some other error occurred.
                pass
            count = count or 0
            run['counts'].append(int(count))

        for total in totals:
            try:
                # Get the string of the tally count.
                count = redis.get('runs:%s:totals:%s:%s'
                                  % (run_key, precision, total))
            except:
                # Maybe this key is not a set - or some other error occurred.
                pass
            count = count or 0
            run['counts'].append(int(count))

        runs.append(run)

    return {
        'precision': precision,
        'moods': moods,
        'totals': totals,
        'runs': runs
    }


def _generate_csv(precision):
    columns = ['timestamp'] + moods
    lines = [','.join(columns)]

    # Get sorted set in descending order by date.
    runs = redis.zrevrange('runs', 0, -1, 1)

    for run_timestamp, run_key in runs:
        # This is the value of the run which we key off of
        # (e.g., 20130116233651).
        run_key = str(int(run_key))

        line = [run_timestamp]

        for mood in moods:
            try:
                # Get the string of the mood count.
                count = redis.get('runs:%s:moods:%s:%s'
                                  % (run_key, precision, mood))
            except:
                pass
            count = count or 0
            line.append(str(count))

        lines.append(','.join(line))

    return '\n'.join(lines)


@app.route('/csv/exact')
def csv_exact():
    return Response(_generate_csv('exact'), mimetype='text/plain')


@app.route('/csv/exact.csv')
def csv_exact_download():
    return Response(_generate_csv('exact'), mimetype='text/csv')


@app.route('/csv/fuzzy')
def csv_fuzzy():
    return Response(_generate_csv('fuzzy'), mimetype='text/plain')


@app.route('/csv/fuzzy.csv')
def csv_fuzzy_download():
    return Response(_generate_csv('fuzzy'), mimetype='text/csv')


if __name__ == '__main__':
    debug = bool(os.environ.get('DEBUG'))
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug, host='0.0.0.0', port=port)
