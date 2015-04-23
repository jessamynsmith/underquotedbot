from twitter_bot import Settings

from bot.messages import QuotationProvider
from bot.since_id import RedisProvider


class UnderquotedBotSettings(Settings):
    """ Settings for UnderquotedBot """
    def __init__(self):
        super(UnderquotedBotSettings, self).__init__()
        self.MESSAGE_PROVIDER = QuotationProvider
        self.SINCE_ID_PROVIDER = RedisProvider
