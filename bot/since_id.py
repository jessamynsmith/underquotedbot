import os
import redis

from twitter_bot import SettingsError


class RedisProvider(object):

    def __init__(self, redis_url=None):
        if not redis_url:
            redis_url = os.environ.get('REDISTOGO_URL')
            if not redis_url:
                raise SettingsError("You must supply redis_url or set the REDISTOGO_URL "
                                    "environment variable.")
        self.redis = redis.Redis.from_url(redis_url)

    def get(self):
        since_id = ''
        value = self.redis.get('since_id')
        if value:
            since_id = value.decode('utf8')
        return since_id

    def set(self, since_id):
        return self.redis.set('since_id', since_id)

    def delete(self):
        return self.redis.delete('since_id')
