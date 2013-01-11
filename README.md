mula
==========

Because the mula market should be open.


Installation
============

Requirements:

    * Python 2.7 (`brew install python` using [homebrew](http://mxcl.github.com/homebrew/) for Mac OS X)

Download `virtualenv` and `virtualenvwrapper`:

    curl -s https://raw.github.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | $SHELL

Create a virtual environment:

    mkvirtualenv --no-site-packages --python=$(which python2.7) mula
    workon mula

Acquire dependencies:

    pip install -r requirements.txt

Install redis and its launch agent (Mac OS X):

    brew install redis
    brew info redis

Play with redis:

    redis-cli

Keep an eye on redis:

    redis-cli monitor

To clear redis:

    redis-cli flushall


Development
===========

Run this script:

    DEBUG=1 python tweets.py
