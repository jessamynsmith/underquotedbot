from twitter_bot import Settings

from bot.messages import QuotationProvider
from twitter_bot.since_id.redis_provider import RedisSinceIdProvider


class UnderquotedBotSettings(Settings):
    """ Settings for UnderquotedBot """
    def __init__(self):
        super(UnderquotedBotSettings, self).__init__()
        self.MESSAGE_PROVIDER = QuotationProvider
        self.SINCE_ID_PROVIDER = RedisSinceIdProvider
