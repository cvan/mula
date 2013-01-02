import os

from redis import Redis

try:
    if os.environ.get('DEBUG'):
        import settings_local as settings
    else:
        import settings_prod as settings
except ImportError:
    import settings


redis_env = os.environ.get('REDISTOGO_URL')

if redis_env:
    redis = Redis.from_url(redis_env)
elif getattr(settings, 'REDIS_URL', None):
    redis = Redis.from_url(settings.REDIS_URL)
else:
    redis = Redis(host=settings.REDIS_HOST,
                  port=settings.REDIS_PORT,
                  db=settings.REDIS_DB,
                  password=settings.REDIS_PASS)
