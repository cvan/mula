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


Deployment
==========

To create your app on dotcloud (you should need to do this only the first time):

    dotcloud create novelstocks

To connect to the dotcloud instance:

    dotcloud connect novelstocks

To push code to dotcloud:

    dotcloud push

After the code has been updated it'll print out the URL, for example:

    http://novelstocks-hywnaqan.dotcloud.com

To SSH into the dotcloud instance to fire off a run:

    dotcloud run www && cd current
    screen
    python tweets.py

To detach a screen session from Terminal:

    holding control, press A, then press D

To view open screen sessions:

    screen -list

To re-attach a screen session:

    screen -raAd 229

To view the logs:

    tail -f /var/log/supervisor/uwsgi.log

To view the redis connection info:

    dotcloud info data

Updating code:

    dotcloud push && dotcloud run www && cd current
    screen
    python tweets.py
    holding control, press A, then press D
    logout

Then view in your browser:

    http://novelstocks-hywnaqan.dotcloud.com

To check on the jobs:

    dotcloud push && dotcloud run www && cd current
    screen -list
    screen -raAd <number of session>
