mula
==========

Because the mula market should be open.


Installation
============

Requirements:

    * Python 2.7 (`brew install python` using [homebrew](http://mxcl.github.com/homebrew/) for Mac OS X)

Download `virtualenv` and `virtualenvwrapper`:

    curl -s https://raw.github.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | $SHELL
    source ~/.bashrc

Create a virtual environment:

    mkvirtualenv --no-site-packages --python=$(which python2.7) mula
    workon mula

Acquire dependencies:

    pip install -r requirements.txt

Install redis and its launch agent (Mac OS X):

    brew install redis
    brew info redis


Development
===========

To get new dependencies:

    pip install -r requirements.txt

To do a run:

    DEBUG=1 python tweets.py

To run your web server:

    DEBUG=1 python app.py

To view the reports of the runs, load these in your web browser:

    http://localhost:5000/
    http://localhost:5000/csv/fuzzy
    http://localhost:5000/csv/exact
    http://localhost:5000/csv/fuzzy.csv
    http://localhost:5000/csv/exact.csv

To play with redis:

    redis-cli

To keep an eye on the commands being sent to redis:

    redis-cli monitor

To clear your redis database:

    redis-cli flushall
