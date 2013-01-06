mula
==========

Because the mula market should be open.


Installation
============

Download virtualenv:

    pip install virtualenv

Create a virtual environment:

    mkvirtualenv --distribute --no-site-packages mula
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
