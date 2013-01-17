"""
Make a `settings_local.py` if you want to override these settings.
"""

import os


DEBUG = os.environ.get('DEBUG', False)
MOCK = os.environ.get('MOCK', False)

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = None
REDIS_PASS = None
