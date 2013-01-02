#!/usr/bin/env python

import collections
import datetime
import itertools
import re

import redis
from nltk.corpus import wordnet

from common import redis


strip_whitespace = lambda x: re.sub('\s+', ' ', x).strip()

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

search_terms = [strip_whitespace(x.replace('{mood}', '')) for x in sentiments]

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

mood_synonyms = {}
for mood in moods:
    # Notice that the original mood word is returned by `synsets`.
    cached = redis.smembers('synonyms:%s' % mood)
    if cached:
        # This is already in redis DB, so we're good.
        mood_synonyms[mood] = cached
    else:
        all_synonyms = [x.lemma_names for x in wordnet.synsets(mood)]

        # Flatten the lists of lists, and return the unique words.
        synonyms = set(itertools.chain.from_iterable(all_synonyms))

        # Store it in redis DB, so we don't have to a lookup next time.
        for synonym in synonyms:
            redis.sadd('synonyms:%s' % mood, synonym)

        mood_synonyms[mood] = synonyms


def run():
    # When the run started.
    timestamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print timestamp

    tweets = get_tweets()
    print get_counts(tweets)


def get_tweets():
    # Sample tweets.
    tweets = [
        'i am so hostile',
        'im blue about this',
    ]
    return tweets


def get_counts(tweets):
    # All totals default to 0.
    counts = collections.Counter()

    for tweet in tweets:
        tweet = strip_whitespace(tweet)

        # Keep track of the mood counts per tweet.
        mood_counts = get_mood_counts(tweet)

        if mood_counts:
            mood_counts['total'] = 1
            counts.update(mood_counts)

    return dict(counts)


def get_mood_counts(tweet):
    tweet_counts = {}

    # Go through all the sentiments.
    for sentiment in sentiments:
        for mood in moods:
            # Get all the synonyms for this mood word.
            words = mood_synonyms.get(mood, set(mood))

            for word in words:
                # Don't record the same mood twice.
                if mood in tweet_counts:
                    continue

                phrase_to_look_for = sentiment.format(mood=word)
                if phrase_to_look_for in tweet:
                    tweet_counts[mood] = 1

    return tweet_counts


if __name__ == '__main__':
    run()
