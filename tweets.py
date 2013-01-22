#!/usr/bin/env python

import collections
import datetime
import json
import os
import re
import time

import requests
from common import redis

try:
    if os.environ.get('DEBUG'):
        import settings_local as settings
    else:
        import settings_prod as settings
except ImportError:
    import settings


strip_whitespace = lambda x: re.sub('\s+', ' ', x).strip()


class Thesaurus(object):
    # Moby's Thesaurus
    filename = 'mthesaur.UTF-8.txt'

    @property
    def words(self):
        if hasattr(self, 'mthesaur_words'):
            return self.mthesaur_words

        lines = open(self.filename).readlines()
        self.mthesaur_words = '\n'.join(lines)

        return self.mthesaur_words

thesaurus = Thesaurus()


def get_synonyms(word):
    lines = thesaurus.words
    start = lines.find('\n%s,' % word)
    lines = lines[start:].strip()

    end = lines.find('\n')
    synonyms = lines[:end]

    return synonyms.strip().split(',')


sentiments = '''
feel {mood}
feel so {mood}
i'm {mood}
i am {mood}
im {mood}
makes me {mood}
made me {mood}
making me {mood}
in a {mood} mood
im so {mood}
i'm so {mood}
i am so {mood}
'''.strip().split('\n')

search_terms = [strip_whitespace(x.format(mood='')) for x in sentiments]

moods = '''
composed
elated
unsure
clearheaded
tired
depressed
guilty
confused
anxious
confident
hostile
agreeable
energetic
'''.strip().split('\n')

mood_roots = {
    'elated': '''
        happy
        satisfied
        pleased
        cheerful
        overjoyed
        '''.strip().split('\n'),
    'depressed': '''
        unhappy
        sad
        blue
        hopeless
        discouraged
        lonely
        miserable
        gloomy
        refreshed
        '''.strip().split('\n'),
    'agreeable': '''
        friendly
        agreeable
        helpful
        forgiving
        kindly
        good-natured
        warm-hearted
        good-tempered
        '''.strip().split('\n'),
    'hostile': '''
        angry
        peeved
        grouchy
        spiteful
        annoyed
        resentful
        bitter
        ready to fight
        rebellious
        furious
        bad-tempered
        '''.strip().split('\n'),
    'energetic': '''
        lively
        full of pep
        vigorous
        energetic
        '''.strip().split('\n'),
    'tired': '''
        worn out
        listless
        fatigued
        exhausted
        sluggish
        weary
        bushed
        '''.strip().split('\n'),
    'confused': '''
        confused
        unable to concentrate
        muddled
        bewildered
        forgetful
        uncertain about things
        '''.strip().split('\n'),
    'clearheaded': '''
        efficient
        alert
        '''.strip().split('\n'),
    'composed': '''
        relaxed
        '''.strip().split('\n'),
    'anxious': '''
        uneasy
        restless
        nervous
        anxious
        terrified
        tense
        shaky
        on edge
        panicky
        '''.strip().split('\n'),
    'confident': '''
        strong
        bold
        powerful
        secure
        confident
        self-assured
        forceful
        '''.strip().split('\n'),
    'unsure': '''
        weak
        timid
        unsure
        self-doubting
        uncertain
        feeble
        unassertive
        '''.strip().split('\n'),
    'guilty': '''
        sorry for things done
        unworthy
        desperate
        helpless
        worthless
        guilty
        '''.strip().split('\n'),
}


mood_synonyms = {}


# Uncomment to print mood synonyms.
# import pprint
# pprint.pprint(mood_synonyms)
# import sys
# sys.exit(1)


def run():
    # When the run started.
    timestamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    redis_timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    print timestamp

    # Sorted Set.
    # key: runs
    # score: redis_timestamp
    # value: timestamp
    redis.zadd('runs', timestamp, redis_timestamp)

    if settings.MOCK:
        counts = {}
        counts['exact'] = {'composed': 1, 'elated': 8, 'energetic': 2, 'tired': 1, 'depressed': 6, 'anxious': 4, 'confident': 1, 'agreeable': 5}
        counts['fuzzy'] = {'composed': 10, 'elated': 80, 'energetic': 20, 'tired': 10, 'depressed': 60, 'anxious': 40, 'confident': 10, 'agreeable': 50}
        #
        # TODO: Add total analyzed, etc.
        #
    else:
        counts = process_tweets(search_terms)
    print counts

    for mood in moods:
        for precision, sub_counts in counts.iteritems():
            # Set.
            # key: runs:<redis_timestamp>:<precision [exact or fuzzy]>:<mood>
            # value: <count>
            redis.set('runs:%s:moods:%s:%s' % (redis_timestamp, precision, mood),
                      sub_counts.get(mood, 0))


def process_tweets(terms):
    # All totals default to 0.
    counts = {'exact': collections.Counter(), 'fuzzy': collections.Counter()}

    tweets_seen = []
    base_url = 'http://search.twitter.com/search.json?q=%s&rpp=99&page=%s&result_type=recent'

    for term in terms:
        if settings.DEBUG:
            print term
        proceed = True
        # Keep iterating until there are no more pages.
        page = 1
        while proceed:
            url = base_url % (term.replace(' ', '+'), page)
            if not settings.MOCK:
                res = requests.get(url, timeout=3)

            try:
                if settings.MOCK:
                    data = {'results': [{'id': 1, 'text': 'feel happy'}], 'next_page': '1'}
                    proceed = False
                else:
                    data = json.loads(res.content)
            except ValueError:
                proceed = False
            else:
                if 'next_page' not in data:
                    proceed = False

            try:
                results = data['results']
            except KeyError:
                # No more pages.
                proceed = False
            else:
                for tweet in results:
                    if tweet['id'] not in tweets_seen:
                        tweets_seen.append(tweet['id'])
                        tweet = strip_whitespace(tweet['text'].lower())

                        # Keep track of the mood counts per tweet.
                        mood_counts = get_mood_counts(tweet)

                        if mood_counts:
                            mood_counts['total_analyzed'] = 1
                        else:
                            mood_counts['total_rejected'] = 1
                        mood_counts['total'] = 1
                        counts['exact'].update(mood_counts['exact'])
                        counts['fuzzy'].update(mood_counts['exact'])
                        if settings.DEBUG:
                            print 'exact:', dict(counts['exact'])
                            print 'fuzzy:', dict(counts['fuzzy'])

            if settings.DEBUG:
                print '\t', '-' * 69
                print '\t', url
                print '\t', len(results)

            page += 1

            # Let Twitter catch its breath.
            if page % 5 == 0:
                time.sleep(1)

        time.sleep(1)

    return counts


def get_mood_counts(tweet):
    tweet_counts = {'exact': {}, 'fuzzy': {}}

    # Go through all the sentiment phrases (e.g., "I feel so {mood}").
    for sentiment in sentiments:

        # Go through all the moods (e.g., "depressed").
        for mood in moods:
            # Get all the synonyms for this mood word.
            words = mood_synonyms.get(mood, set(mood))
            words = filter(None, words)

            for word in words:
                # See if we find this phrase in the tweet.
                phrase_to_look_for = sentiment.format(mood=word)
                if phrase_to_look_for in tweet:
                    tweet_counts['exact'][mood] = 1

                # See if the word appears anywhere in the tweet.
                if word in tweet:
                    tweet_counts['fuzzy'][mood] = 1

    return tweet_counts


def build_synonyms():
    for mood in moods:
        # Notice that the original mood word is returned by `synsets`.
        cached = redis.smembers('synonyms:%s' % mood)
        if cached:
            # This is already in redis DB, so we're good.
            mood_synonyms[mood] = cached
        else:
            synonyms = get_synonyms(mood)
            if mood in mood_roots:
                for root in mood_roots[mood]:
                    synonyms += get_synonyms(root)

            # Make this a sorted alphabetical list of unique synonyms.
            synonyms = sorted(list(set(synonyms)))
            # Remove any blank values.
            synonyms = filter(None, synonyms)

            # Store it in redis DB, so we don't have to a lookup next time.
            for synonym in synonyms:
                redis.sadd('synonyms:%s' % mood, synonym)

            mood_synonyms[mood] = synonyms


if __name__ == '__main__':
    build_synonyms()
    run()
